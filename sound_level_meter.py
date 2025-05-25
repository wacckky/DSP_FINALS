import streamlit as st
import numpy as np
import librosa
import librosa.display
import matplotlib.pyplot as plt
import altair as alt

st.set_page_config(page_title="Sound Level Meter", layout="wide")
st.title("🔊 Real-Time Sound Level Meter")

uploaded_file = st.file_uploader("Upload an audio file", type=["wav", "mp3", "ogg"])

if uploaded_file:
    st.audio(uploaded_file)
    y, sr = librosa.load(uploaded_file, sr=None)

    # Frame size and hop length for "real-time" simulation
    frame_size = 2048
    hop_length = 512

    # Compute RMS values per frame
    rms = librosa.feature.rms(y=y, frame_length=frame_size, hop_length=hop_length)[0]
    times = librosa.frames_to_time(np.arange(len(rms)), sr=sr, hop_length=hop_length)

    # Convert to decibels
    db = 20 * np.log10(rms + 1e-6)

    # Optional smoothing: simple moving average
    window = 5
    smooth_db = np.convolve(db, np.ones(window) / window, mode='same')

    # Peak hold: highlight peak level
    peak_db = np.max(db)

    st.subheader("📊 dB Level Over Time (with smoothing)")

    chart_data = {
        "Time (s)": times,
        "dB Level": smooth_db
    }

    df = alt.Chart(alt.Data(values=[{"x": t, "y": d} for t, d in zip(times, smooth_db)])).mark_line().encode(
        x="x:Q",
        y="y:Q"
    ).properties(width=800, height=400).interactive()

    st.altair_chart(df)

    st.metric("📈 Peak dB", f"{peak_db:.2f} dB")
