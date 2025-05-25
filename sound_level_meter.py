import streamlit as st
import numpy as np
import io
import soundfile as sf
import librosa
import altair as alt
from streamlit_webrtc import webrtc_streamer
import av

st.set_page_config(page_title="Sound Level Meter", layout="wide")
st.title("🔊 Real-Time Sound Level Meter")

# --- Section 1: Audio File Upload & dB Level Plot ---

uploaded_file = st.file_uploader("Upload an audio file", type=["wav", "mp3", "ogg"])

if uploaded_file:
    st.audio(uploaded_file)
    # Read uploaded file into memory and load audio
    data, samplerate = sf.read(io.BytesIO(uploaded_file.read()))
    y = data.T if data.ndim > 1 else data  # Handle stereo by taking transpose
    sr = samplerate

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

    df = alt.Chart(alt.Data(values=[{"x": t, "y": d} for t, d in zip(times, smooth_db)])).mark_line().encode(
        x="x:Q",
        y="y:Q"
    ).properties(width=800, height=400).interactive()

    st.altair_chart(df)

    st.metric("📈 Peak dB", f"{peak_db:.2f} dB")

st.markdown("---")

# --- Section 2: Live Microphone Audio Recorder with Tips ---

st.header("🎤 Live Microphone Audio Recorder")

st.markdown("""
- Make sure your microphone is connected and selected.
- When prompted, **allow microphone access** in your browser.
- Use a headset or external mic for better quality.
""")

def audio_frame_callback(frame: av.AudioFrame) -> av.AudioFrame:
    audio = frame.to_ndarray(format="flt32")
    rms = np.sqrt(np.mean(audio**2))
    db = 20 * np.log10(rms + 1e-6)

    # Smooth the dB reading using exponential moving average
    if 'last_db' not in st.session_state:
        st.session_state.last_db = db
    else:
        st.session_state.last_db = 0.9 * st.session_state.last_db + 0.1 * db

    return frame

webrtc_ctx = webrtc_streamer(
    key="mic-recorder",
    mode="sendrecv",
    audio_frame_callback=audio_frame_callback,
    media_stream_constraints={"audio": True, "video": False},
)

if webrtc_ctx.state.playing:
    last_db = st.session_state.get('last_db', None)
    if last_db is not None:
        st.write(f"🔊 Current microphone audio level (dB): {last_db:.1f}")
else:
    st.write("🎙️ Microphone inactive. Click Start and allow mic access when prompted.")
