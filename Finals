!pip install streamlit pydub numpy
# sound_level_meter.py

import streamlit as st
from pydub import AudioSegment
import numpy as np
import io

st.set_page_config(page_title="Sound Level Meter", layout="centered")

st.title("🎧 Sound Level Meter")
st.write("Upload an audio file and measure its sound level (in dB).")

uploaded_file = st.file_uploader("Upload Audio", type=["mp3", "wav", "ogg"])

if uploaded_file is not None:
    st.audio(uploaded_file)

    # Load audio with pydub
    audio = AudioSegment.from_file(uploaded_file)
    samples = np.array(audio.get_array_of_samples())

    # Normalize samples if stereo
    if audio.channels == 2:
        samples = samples.reshape((-1, 2))
        samples = samples.mean(axis=1)

    # Compute RMS and dB
    rms = np.sqrt(np.mean(samples**2))
    db = 20 * np.log10(rms / (2**15)) if rms > 0 else -np.inf

    st.markdown(f"**Duration:** {audio.duration_seconds:.2f} seconds")
    st.markdown(f"**Sample Rate:** {audio.frame_rate} Hz")
    st.markdown(f"**Channels:** {audio.channels}")
    st.markdown(f"**Sound Level:** `{db:.2f} dB` (RMS-based)")

    # Optional: Show waveform or loudness level over time
