import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Mic dB Level", layout="centered")
st.title("🎤 Live Microphone dB Meter")
st.write("This uses your **browser mic**. Grant permission when prompted.")

# Embed the hosted mic dB meter
components.iframe("https://wacckky.github.io/host/", height=200)
