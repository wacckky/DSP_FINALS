import streamlit as st
import streamlit.components.v1 as components
import mic_component

st.set_page_config(page_title="Live Mic dB Level", layout="centered")
st.title("🎤 Live Microphone dB Meter (Web-Based)")
st.write("This uses your browser microphone. Grant permission when prompted.")

db_level = mic_component.mic_db_component()
if db_level is not None:
    st.metric("Current dB", f"{db_level:.2f} dB")
