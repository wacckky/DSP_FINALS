import streamlit as st
import numpy as np
import tempfile
import librosa
import altair as alt
import matplotlib.pyplot as plt
from streamlit_webrtc import webrtc_streamer, WebRtcMode
import av

st.set_page_config(page_title="🔊 Sound Meter", layout="wide")
st.title("🔊 Real-Time Sound Level Meter")

# Choose Input
option = st.radio("Choose Input Method:", ["Upload Audio File", "Use Microphone"])

# Function to analyze and plot audio
def analyze_audio(y, sr):
    frame_size = 2048
    hop_length = 512
    rms = librosa.feature.rms(y=y, frame_length=frame_size, hop_length=hop_length)[0]
    times = librosa.frames_to_time(np.arange(len(rms)), sr=sr, hop_length=hop_length)
    db = 20 * np.log10(rms + 1e-6)
    smooth_db = np.convolve(db, np.ones(5)/5, mode='same')
    peak_db = np.max(db)

    st.subheader("📊 dB Level Over Time")
    db_chart = alt.Chart(alt.Data(values=[
        {"x": t, "y": d} for t, d in zip(times, smooth_db)
    ])).mark_line().encode(
        x=alt.X("x:Q", title="Time (s)"),
        y=alt.Y("y:Q", title="dB Level")
    ).properties(width=800, height=400)
    st.altair_chart(db_chart)
    st.metric("📈 Peak dB", f"{peak_db:.2f} dB")

    # Frequency spectrum
    st.subheader("🎶 Frequency Spectrum")
    fft = np.abs(np.fft.rfft(y))
    freqs = np.fft.rfftfreq(len(y), 1/sr)
    fig, ax = plt.subplots()
    ax.plot(freqs, fft)
    ax.set_xlabel("Frequency (Hz)")
    ax.set_ylabel("Amplitude")
    st.pyplot(fig)

# ------------------ Upload Section ------------------

if option == "Upload Audio File":
    uploaded_file = st.file_uploader("Upload .wav/.mp3/.ogg", type=["wav", "mp3", "ogg"])
    if uploaded_file:
        st.audio(uploaded_file)
        if st.button("🔍 Analyze Audio"):
            with tempfile.NamedTemporaryFile(suffix=".wav") as tmp:
                tmp.write(uploaded_file.read())
                tmp.flush()
                y, sr = librosa.load(tmp.name, sr=None)
                analyze_audio(y, sr)

# ------------------ Microphone Section ------------------

elif option == "Use Microphone":
    st.markdown("🎤 Click **Start** and allow microphone access.")

    # Session State Init
    if "mic_buffer" not in st.session_state:
        st.session_state.mic_buffer = np.array([], dtype=np.float32)
    if "recording_stopped" not in st.session_state:
        st.session_state.recording_stopped = False
    if "was_playing" not in st.session_state:
        st.session_state.was_playing = False

    def mic_callback(frame: av.AudioFrame) -> av.AudioFrame:
        audio = frame.to_ndarray(format="flt32")
        mono = audio.mean(axis=0)
        st.session_state.mic_buffer = np.concatenate((st.session_state.mic_buffer, mono))
        return frame

    # Start mic stream
    webrtc_ctx = webrtc_streamer(
        key="mic-stream",
        mode=WebRtcMode.SENDRECV,
        audio_frame_callback=mic_callback,
        media_stream_constraints={"audio": True, "video": False},
    )

    # Track mic state transition
    if webrtc_ctx.state.playing:
        st.session_state.was_playing = True
        st.session_state.recording_stopped = False
    elif st.session_state.was_playing and not webrtc_ctx.state.playing:
        st.session_state.recording_stopped = True

    # Show analysis options after stop
    if st.session_state.recording_stopped and st.session_state.mic_buffer.size > 0:
        st.success("✅ Recording complete.")
        col1, col2 = st.columns(2)

        if col1.button("🔍 Analyze Recording"):
            y = st.session_state.mic_buffer
            sr = 16000  # Assuming mic records at 16kHz
            analyze_audio(y, sr)

        if col2.button("🔁 Retake"):
            st.session_state.mic_buffer = np.array([], dtype=np.float32)
            st.session_state.recording_stopped = False
            st.session_state.was_playing = False
            st.experimental_rerun()
