import streamlit as st
import sounddevice as sd
import numpy as np
import threading
import time

# Streamlit page config
st.set_page_config(page_title="Real-Time Sound Level Meter", layout="centered")

st.title("🎤 Real-Time Sound Level Meter")
st.write("This app measures real-time sound levels from your microphone in decibels (dB).")

# Global variable to store dB level
sound_level = st.empty()

# Streamlit checkbox to toggle measurement
start_measurement = st.checkbox("Start Measuring")

# Parameters
duration = 0.2  # in seconds
sample_rate = 44100

def calculate_rms(block):
    return np.sqrt(np.mean(block**2))

def audio_callback(indata, frames, time, status):
    global db_level
    if status:
        print(status)
    rms = calculate_rms(indata)
    db_level = 20 * np.log10(rms + 1e-6)  # avoid log(0)

def audio_thread():
    with sd.InputStream(callback=audio_callback, channels=1, samplerate=sample_rate, blocksize=int(duration * sample_rate)):
        while start_measurement:
            time.sleep(duration)
            sound_level.metric(label="Current dB Level", value=f"{db_level:.2f} dB")

if start_measurement:
    db_level = 0.0
    t = threading.Thread(target=audio_thread)
    t.start()
else:
    st.write("👈 Click the checkbox to start measuring.")

