import streamlit as st
from streamlit.components.v1 import html

st.set_page_config(page_title="Mic dB Level", layout="centered")

st.markdown(
    """
    <style>
    .stApp {
        background-color: black !important;
        color: white !important;
    }
    .streamlit-title {
        font-size: 3em !important;
        font-weight: bold !important;
        color: white !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<h1 class="streamlit-title">Sound Level Meter</h1>', unsafe_allow_html=True)

meter_html = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<style>
  @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@600&display=swap');

  html, body {
    margin: 0; padding: 0;
    background: transparent;
    font-family: 'Poppins', sans-serif;
    color: white;
    user-select: none;
  }

  #app-container {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 550px;
    max-width: 500px;
    margin: 50px auto 0;
    position: relative;
  }

  #labels {
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    height: 500px;
    font-size: 0.875rem;
    font-weight: 500;
    margin-right: 5px;
  }

  .label {
    display: flex;
    align-items: center;
    color: white;
    gap: 5px;
  }

  .tick {
    width: 20px;
    height: 2px;
    background-color: #9ca3af;
  }

  .red { color: #ef4444; }
  .yellow { color: #facc15; }
  .green { color: #10b981; }

  #meter-wrapper {
    position: relative;
    width: 50px;
    height: 500px;
    border-radius: 14px;
    background: #1f2937;
    border: 2px solid #374151;
    overflow: hidden;
    margin: 0 10px;
    display: flex;
    align-items: flex-end;
    box-shadow: inset 0 0 10px rgba(0,0,0,0.6), 0 4px 12px rgba(0,0,0,0.4);
  }

  #bar {
    width: 100%;
    height: 0%;
    border-radius: 14px 14px 0 0;
    background: linear-gradient(to top, #ef4444, #facc15, #10b981);
    box-shadow: 0 0 15px 4px rgba(255, 0, 0, 0.4);
    transition: height 0.2s ease-out;
  }

  #db-stats {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    justify-content: center;
  }

  #avg-db, #max-db {
    font-size: 0.9rem;
    color: #9ca3af;
  }

  #db-value {
    font-weight: 700;
    font-size: 1.1rem;
    color: #ffffff;
  }

  #out-message {
    color: #ef4444;
    font-weight: 600;
    margin-top: 15px;
    text-align: center;
  }

  .overlay {
    position: absolute;
    z-index: 10;
    top: 0; left: 0;
    width: 100%;
    height: 100%;
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    background: rgba(0, 0, 0, 0.4);
    display: flex;
    justify-content: center;
    align-items: center;
    flex-direction: column;
  }

  .overlay button {
    padding: 10px 24px;
    font-size: 1.2rem;
    background: #10b981;
    color: white;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    transition: background 0.3s ease;
  }

  .overlay button:hover {
    background: #059669;
  }

  #reset-button {
    margin-top: 10px;
    font-size: 0.8rem;
    padding: 4px 12px;
    background: #e5e7eb;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    color: black;
  }
</style>
</head>
<body>

  <div id="app-container">
    <div id="labels">
      <div class="label red"><div class="tick"></div><span>130</span></div>
      <div class="label red"><div class="tick"></div><span>120</span></div>
      <div class="label red"><div class="tick"></div><span>110</span></div>
      <div class="label yellow"><div class="tick"></div><span>100</span></div>
      <div class="label yellow"><div class="tick"></div><span>90</span></div>
      <div class="label yellow"><div class="tick"></div><span>80</span></div>
      <div class="label green"><div class="tick"></div><span>70</span></div>
      <div class="label green"><div class="tick"></div><span>60</span></div>
      <div class="label green"><div class="tick"></div><span>50</span></div>
      <div class="label green"><div class="tick"></div><span>40</span></div>
      <div class="label green"><div class="tick"></div><span>30</span></div>
      <div class="label green"><div class="tick"></div><span>20</span></div>
      <div class="label green"><div class="tick"></div><span>10</span></div>
    </div>

    <div id="meter-wrapper">
      <div id="bar"></div>
    </div>

    <div id="db-stats">
      <div id="avg-db">Avg: 0 dB</div>
      <div id="max-db">Max: 0 dB</div>
      <div id="db-value">dB: 0</div>
      <button id="reset-button">Reset</button>
    </div>

    <div class="overlay" id="overlay">
      <button onclick="startApp()">Start</button>
    </div>
  </div>
  <div id="out-message"></div>

<script>
function startApp() {
  document.getElementById("overlay").style.display = "none";
}
</script>
</body>
</html>
"""

html(meter_html, height=600, scrolling=False)
