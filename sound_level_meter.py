import streamlit as st
from audiorecorder import audiorecorder
import numpy as np
import librosa
import altair as alt
import matplotlib.pyplot as plt
import tempfile
import soundfile as sf

st.set_page_config(page_title="Sound Level Analyzer", layout="wide")
st.title("🔊 Audio Analyzer: Upload or Record")

# Initialize session state
if "audio_data" not in st.session_state:
    st.session_state.audio_data = None
if "audio_ready" not in st.session_state:
    st.session_state.audio_ready = False
if "analyzed" not in st.session_state:
    st.session_state.analyzed = False

# --- Option Selection ---
option = st.radio("Choose audio input method:", ["📤 Upload Audio File", "🎤 Record with Microphone"])

# --- Upload Option ---
if option == "📤 Upload Audio File":
    uploaded_file = st.file_uploader("Upload a WAV, MP3, or OGG file", type=["wav", "mp3", "ogg"])
    if uploaded_file:
        st.audio(uploaded_file)
        st.session_state.audio_data = uploaded_file.read()
        st.session_state.audio_ready = True
        st.session_state.analyzed = False
        st.success("✅ File uploaded!")

# --- Record Option ---
elif option == "🎤 Record with Microphone":
    audio = audiorecorder("Start Recording", "Stop Recording")
    if len(audio) > 0:
        st.audio(audio.tobytes(), format="audio/wav")
        st.session_state.audio_data = audio.tobytes()
        st.session_state.audio_ready = True
        st.session_state.analyzed = False
        st.success("✅ Recording complete!")

# --- Analyze Button ---
if st.session_state.audio_ready and not st.session_state.analyzed:
    if st.button("🔍 Analyze Audio"):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmpfile:
            tmpfile.write(st.session_state.audio_data)
            tmpfile.flush()
            y, sr = librosa.load(tmpfile.name, sr=None)

        # --- dB Analysis ---
        st.subheader("📊 dB Level Over Time")
        frame_size = 2048
        hop_length = 512
        rms = librosa.feature.rms(y=y, frame_length=frame_size, hop_length=hop_length)[0]
        times = librosa.frames_to_time(np.arange(len(rms)), sr=sr, hop_length=hop_length)
        db = 20 * np.log10(rms + 1e-6)
        smooth_db = np.convolve(db, np.ones(5)/5, mode='same')
        peak_db = np.max(db)

        db_chart = alt.Chart(alt.Data(values=[
            {"x": t, "y": d} for t, d in zip(times, smooth_db)
        ])).mark_line().encode(
            x=alt.X("x:Q", title="Time (s)"),
            y=alt.Y("y:Q", title="dB Level")
        ).properties(width=800, height=400)
        st.altair_chart(db_chart)
        st.metric("📈 Peak dB", f"{peak_db:.2f} dB")

        # --- Frequency Spectrum ---
        st.subheader("🎶 Frequency Spectrum")
        fft = np.abs(np.fft.rfft(y))
        freqs = np.fft.rfftfreq(len(y), 1/sr)
        fig, ax = plt.subplots()
        ax.plot(freqs, fft)
        ax.set_xlabel("Frequency (Hz)")
        ax.set_ylabel("Amplitude")
        ax.set_xlim(0, 8000)
        st.pyplot(fig)

        st.session_state.analyzed = True

# --- Retake / Reset ---
if st.session_state.audio_ready:
    if st.button("🔁 Retake or Upload New"):
        st.session_state.audio_ready = False
        st.session_state.analyzed = False
        st.session_state.audio_data = None
        st.experimental_rerun()
