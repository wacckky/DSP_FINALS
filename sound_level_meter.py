import streamlit as st
import numpy as np
import librosa

st.title("🔊 Sound Level Meter")

uploaded_file = st.file_uploader("Upload an audio file", type=["wav", "mp3", "ogg"])

if uploaded_file is not None:
    st.audio(uploaded_file)

    # Load audio with librosa
    y, sr = librosa.load(uploaded_file, sr=None, mono=True)

    # Calculate RMS
    rms = np.sqrt(np.mean(y**2))
    db = 20 * np.log10(rms) if rms > 0 else -np.inf

    st.write(f"**Sample Rate:** {sr} Hz")
    st.write(f"**Duration:** {len(y)/sr:.2f} seconds")
    st.write(f"### 🔉 Sound Level: `{db:.2f} dB`")
