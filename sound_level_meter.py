import streamlit as st
import sounddevice as sd
import numpy as np
import time

st.set_page_config(page_title="Real-Time Sound Level Meter", layout="centered")
st.title("🎤 Real-Time Sound Level Meter")

st.write("This app uses your microphone to measure and plot real-time dB levels.")

# Settings
duration = 0.2  # seconds
sample_rate = 44100
window_size = 30  # number of readings shown in chart

# Initialize placeholders
start_button = st.button("Start Measuring")
chart = st.line_chart()
db_display = st.empty()

def calculate_db(indata):
    rms = np.sqrt(np.mean(indata**2))
    db = 20 * np.log10(rms + 1e-6)  # +1e-6 to avoid log(0)
    return db

def measure_sound():
    db_levels = []

    with sd.InputStream(channels=1, samplerate=sample_rate, blocksize=int(sample_rate * duration)) as stream:
        while True:
            try:
                audio_data, _ = stream.read(int(sample_rate * duration))
                db = calculate_db(audio_data)
                db_levels.append(db)

                # Keep only recent values
                if len(db_levels) > window_size:
                    db_levels.pop(0)

                # Update UI
                chart.line_chart(db_levels)
                db_display.metric("Current dB", f"{db:.2f} dB")
                time.sleep(duration)
            except Exception as e:
                st.error(f"Error: {e}")
                break

if start_button:
    st.info("🔴 Measuring live... speak into your microphone.")
    measure_sound()
