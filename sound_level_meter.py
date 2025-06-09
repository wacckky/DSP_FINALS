import streamlit as st
import numpy as np
import tempfile
import librosa
import altair as alt
from streamlit_webrtc import webrtc_streamer, WebRtcMode
import av
import matplotlib.pyplot as plt

st.set_page_config(page_title="Sound Level Meter", layout="wide")
st.title("🔊 Real-Time Sound Level Meter")

# --- Step 1: Choose Input Method ---
option = st.radio("Choose Input Method:", ["Upload Audio File", "Use Microphone"])

# --- Step 2A: Audio File Upload ---
if option == "Upload Audio File":
    uploaded_file = st.file_uploader("Upload an audio file", type=["wav", "mp3", "ogg"])

    if uploaded_file:
        st.audio(uploaded_file)

        # Analyze button
        if st.button("🔍 Analyze Audio"):
            with tempfile.NamedTemporaryFile(suffix=".wav") as tmp_file:
                tmp_file.write(uploaded_file.read())
                tmp_file.flush()
                y, sr = librosa.load(tmp_file.name, sr=None)

            # Frame and hop sizes
            frame_size = 2048
            hop_length = 512

            # Compute RMS and dB
            rms = librosa.feature.rms(y=y, frame_length=frame_size, hop_length=hop_length)[0]
            times = librosa.frames_to_time(np.arange(len(rms)), sr=sr, hop_length=hop_length)
            db = 20 * np.log10(rms + 1e-6)
            smooth_db = np.convolve(db, np.ones(5) / 5, mode='same')
            peak_db = np.max(db)

            st.subheader("📊 dB Level Over Time")
            df = alt.Chart(alt.Data(values=[{"x": t, "y": d} for t, d in zip(times, smooth_db)]))\
                .mark_line().encode(
                    x=alt.X("x:Q", title="Time (s)"),
                    y=alt.Y("y:Q", title="dB Level")
                ).properties(width=800, height=400).interactive()
            st.altair_chart(df)
            st.metric("📈 Peak dB", f"{peak_db:.2f} dB")

            # Frequency Analysis
            st.subheader("🎶 Frequency Spectrum")
            fft = np.abs(np.fft.rfft(y))
            freqs = np.fft.rfftfreq(len(y), 1 / sr)

            fig, ax = plt.subplots()
            ax.plot(freqs, fft)
            ax.set_xlabel("Frequency (Hz)")
            ax.set_ylabel("Amplitude")
            ax.set_title("Frequency Spectrum")
            st.pyplot(fig)

# --- Step 2B: Microphone Input ---
elif option == "Use Microphone":
    st.header("🎤 Live Microphone Monitor")
    st.markdown("Click **Start** and allow microphone access.")

    # Initialize session state variables
    if "db_history" not in st.session_state:
        st.session_state.db_history = []
    if "audio_buffer" not in st.session_state:
        st.session_state.audio_buffer = np.array([], dtype=np.float32)
    if "last_db" not in st.session_state:
        st.session_state.last_db = 0.0
    if "show_buttons" not in st.session_state:
        st.session_state.show_buttons = False

    def audio_frame_callback(frame: av.AudioFrame) -> av.AudioFrame:
        audio = frame.to_ndarray(format="flt32")
        audio_mono = audio.mean(axis=0)  # Convert to mono
        rms = np.sqrt(np.mean(audio_mono**2))
        db = 20 * np.log10(rms + 1e-6)

        st.session_state.last_db = 0.9 * st.session_state.last_db + 0.1 * db
        t = len(st.session_state.db_history) / 20
        st.session_state.db_history.append((t, st.session_state.last_db))
        st.session_state.audio_buffer = np.concatenate([st.session_state.audio_buffer, audio_mono])

        return frame

    webrtc_ctx = webrtc_streamer(
        key="mic-recorder",
        mode=WebRtcMode.SENDRECV,
        audio_frame_callback=audio_frame_callback,
        media_stream_constraints={"audio": True, "video": False},
    )

    if webrtc_ctx.state.playing:
        st.write(f"🎚️ Live dB Level: **{st.session_state.last_db:.2f} dB**")
        st.session_state.show_buttons = True

    # Analyze or Retake Buttons
    if st.session_state.show_buttons:
        col1, col2 = st.columns(2)
        with col1:
            analyze = st.button("🔍 Analyze")
        with col2:
            retake = st.button("🔁 Retake")

        if analyze and len(st.session_state.db_history) > 0:
            st.subheader("📊 Analyzed dB Over Time")
            data = [{"x": t, "y": d} for t, d in st.session_state.db_history]
            chart = alt.Chart(alt.Data(values=data)).mark_line().encode(
                x=alt.X("x:Q", title="Time (s)"),
                y=alt.Y("y:Q", title="dB Level")
            ).properties(width=800, height=400).interactive()
            st.altair_chart(chart)

            peak = max(d for _, d in st.session_state.db_history)
            st.metric("📈 Peak dB", f"{peak:.2f} dB")

            st.subheader("🎶 Frequency Spectrum from Mic")
            audio_data = st.session_state.audio_buffer
            if len(audio_data) > 0:
                fft = np.abs(np.fft.rfft(audio_data))
                freqs = np.fft.rfftfreq(len(audio_data), 1 / 16000)  # Assume 16kHz

                fig, ax = plt.subplots()
                ax.plot(freqs, fft)
                ax.set_xlabel("Frequency (Hz)")
                ax.set_ylabel("Amplitude")
                ax.set_title("Frequency Spectrum")
                st.pyplot(fig)

        if retake:
            st.session_state.db_history = []
            st.session_state.audio_buffer = np.array([], dtype=np.float32)
            st.session_state.last_db = 0.0
            st.session_state.show_buttons = False
            st.experimental_rerun()
