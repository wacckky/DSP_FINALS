import streamlit as st
import numpy as np
import librosa
import altair as alt
import sounddevice as sd
import queue
import threading
import time

st.set_page_config(page_title="Real-Time Sound Level Meter", layout="wide")
st.title("🔊 Real-Time Sound Level Meter with Scrolling Chart")

MODE = st.sidebar.radio("Input mode:", ["Upload Audio File", "Microphone Live"])

# Parameters for RMS computation
FRAME_SIZE = 2048
HOP_LENGTH = 512
WINDOW_SIZE = 100  # Number of points to show on the scrolling chart (~recent values)

def compute_db(y):
    rms = librosa.feature.rms(y=y, frame_length=FRAME_SIZE, hop_length=HOP_LENGTH)[0]
    db = 20 * np.log10(rms + 1e-6)
    return db

# --- Upload Audio File Mode ---
if MODE == "Upload Audio File":
    uploaded_file = st.file_uploader("Upload an audio file", type=["wav", "mp3", "ogg"])
    if uploaded_file is not None:
        st.audio(uploaded_file)
        y, sr = librosa.load(uploaded_file, sr=None)

        db = compute_db(y)

        times = librosa.frames_to_time(np.arange(len(db)), sr=sr, hop_length=HOP_LENGTH)

        # Scrolling window start index, controlled by slider
        max_start = max(0, len(db) - WINDOW_SIZE)
        start_idx = st.slider("Scroll through time (seconds)", 0, max_start, max_start)

        chart_data = [{"Time (s)": times[i], "dB Level": db[i]} for i in range(start_idx, start_idx + WINDOW_SIZE)]
        df = alt.Data(values=chart_data)

        chart = alt.Chart(df).mark_line().encode(
            x='Time (s):Q',
            y=alt.Y('dB Level:Q', scale=alt.Scale(domain=[-80, 0]))
        ).properties(width=800, height=300)

        st.altair_chart(chart, use_container_width=True)

# --- Microphone Live Mode ---
else:
    st.write("Click Start to begin microphone input.")

    if 'audio_queue' not in st.session_state:
        st.session_state.audio_queue = queue.Queue()
        st.session_state.running = False
        st.session_state.db_values = []
        st.session_state.times = []

    def audio_callback(indata, frames, time_info, status):
        if status:
            print(status)
        st.session_state.audio_queue.put(indata.copy())

    def audio_thread():
        with sd.InputStream(channels=1, callback=audio_callback, blocksize=HOP_LENGTH):
            while st.session_state.running:
                time.sleep(0.1)

    if st.button("Start Microphone"):
        if not st.session_state.running:
            st.session_state.running = True
            st.session_state.db_values = []
            st.session_state.times = []
            threading.Thread(target=audio_thread, daemon=True).start()

    if st.button("Stop Microphone"):
        st.session_state.running = False

    if st.session_state.running:
        # Collect audio from queue and process
        try:
            while not st.session_state.audio_queue.empty():
                data = st.session_state.audio_queue.get_nowait()
                y = data.flatten()

                rms = np.sqrt(np.mean(y**2))
                db = 20 * np.log10(rms + 1e-6)

                st.session_state.db_values.append(db)
                current_time = time.time()
                st.session_state.times.append(current_time)

                # Keep only recent WINDOW_SIZE points for scrolling
                if len(st.session_state.db_values) > WINDOW_SIZE:
                    st.session_state.db_values.pop(0)
                    st.session_state.times.pop(0)

        except queue.Empty:
            pass

        if st.session_state.db_values:
            times_rel = np.array(st.session_state.times) - st.session_state.times[0]
            chart_data = [{"Time (s)": t, "dB Level": d} for t, d in zip(times_rel, st.session_state.db_values)]

            df = alt.Data(values=chart_data)

            chart = alt.Chart(df).mark_line().encode(
                x='Time (s):Q',
                y=alt.Y('dB Level:Q', scale=alt.Scale(domain=[-80, 0]))
            ).properties(width=800, height=300)

            st.altair_chart(chart, use_container_width=True)

    else:
        st.write("Microphone is stopped.")
