from pydub import AudioSegment
import numpy as np
import streamlit as st

st.title("🎧 Sound Level Meter")
uploaded_file = st.file_uploader("Upload an audio file (.mp3, .wav)", type=["mp3", "wav", "ogg"])

if uploaded_file is not None:
    st.audio(uploaded_file)

    audio = AudioSegment.from_file(uploaded_file)
    samples = np.array(audio.get_array_of_samples())

    # If stereo, average the channels
    if audio.channels == 2:
        samples = samples.reshape((-1, 2))
        samples = samples.mean(axis=1)

    # Convert to float32 for accurate RMS calculation
    samples = samples.astype(np.float32)

    rms = np.sqrt(np.mean(samples ** 2))
    db = 20 * np.log10(rms / 32768) if rms > 0 else -np.inf

    st.markdown(f"**Duration:** {audio.duration_seconds:.2f} seconds")
    st.markdown(f"**Sample Rate:** {audio.frame_rate} Hz")
    st.markdown(f"**Channels:** {audio.channels}")
    st.markdown(f"### Sound Level: `{db:.2f} dB`")
