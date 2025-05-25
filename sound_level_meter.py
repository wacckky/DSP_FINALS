import streamlit as st
import numpy as np
import tempfile
import librosa
import altair as alt
from streamlit_webrtc import webrtc_streamer, WebRtcMode
import av

st.set_page_config(page_title="Sound Level Meter", layout="wide")
st.title("🔊 Real-Time Sound Level Meter")

# --- Section 1: Audio File Upload ---

uploaded_file = st.file_uploader("Upload an audio file", type=["wav", "mp3", "ogg"])

if uploaded_file:
    st.audio(uploaded_file)

    # Save uploaded audio to a temporary file
    with tempfile.NamedTemporaryFile(suffix=".wav") as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_file.flush()
        y, sr = librosa.load(tmp_file.name, sr=None)

    # Frame and hop sizes
    frame_size = 2048
    hop_length = 512

    # Compute RMS and dB
    rms = librosa.feature.rms(y=y, frame_length=frame_size, hop_length=hop_length)[0]
    times = librosa.frames_to_time(np.arange(len(rms)), sr=sr, hop_length=hop_length)
    db = 20 * np.log10(rms + 1e-6)

    # Smoothing
    window = 5
    smooth_db = np.convolve(db, np.ones(window) / window, mode='same')
    peak_db = np.max(db)

    st.subheader("📊 dB Level Over Time (with smoothing)")

    df = alt.Chart(alt.Data(values=[
        {"x": t, "y": d} for t, d in zip(times, smooth_db)
    ])).mark_line().encode(
        x=alt.X("x:Q", title="Time (s)"),
        y=alt.Y("y:Q", title="dB Level")
    ).properties(width=800, height=400).interactive()

    st.altair_chart(df)
    st.metric("📈 Peak dB", f"{peak_db:.2f} dB")

st.markdown("---")

# --- Section 2: Live Microphone Input ---

st.header("🎤 Live Microphone Input Monitor")

st.markdown("""
- Click **Start** and allow your browser to access the microphone.
- Use a headset or external mic for clearer signal.
""")

# Audio frame callback to compute RMS and dB
def audio_frame_callback(frame: av.AudioFrame) -> av.AudioFrame:
    audio = frame.to_ndarray(format="flt32")
    rms = np.sqrt(np.mean(audio**2))
    db = 20 * np.log10(rms + 1e-6)

    # Exponential moving average smoothing
    if "last_db" not in st.session_state:
        st.session_state.last_db = db
    else:
        st.session_state.last_db = 0.9 * st.session_state.last_db + 0.1 * db

    return frame

# Start WebRTC mic stream
webrtc_ctx = webrtc_streamer(
    key="mic-recorder",
    mode=WebRtcMode.SENDRECV,
    audio_frame_callback=audio_frame_callback,
    media_stream_constraints={"audio": True, "video": False},
)

# Display live mic dB
if webrtc_ctx.state.playing:
    last_db = st.session_state.get("last_db", None)
    if last_db is not None:
        st.write(f"🎚️ Live Microphone dB Level: **{last_db:.2f} dB**")
else:
    st.info("🎙️ Click Start and allow microphone access.")
