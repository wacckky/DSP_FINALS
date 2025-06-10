import streamlit as st
from mic_component import mic_db_component  # ✅ use direct import

st.set_page_config(page_title="Live Mic dB Level")
st.title("🎤 Web Mic dB Meter (JS-based)")

db_level = mic_db_component()
if db_level is not None:
    st.metric("Current dB", f"{db_level:.2f} dB")
