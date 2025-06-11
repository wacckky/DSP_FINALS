import streamlit as st
from streamlit.components.v1 import html

st.set_page_config(page_title="Mic dB Level", layout="centered")

# Inject CSS for styling
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

# Embed the custom HTML/CSS/JS dB meter
meter_html = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<style>
  body {
    margin: 0;
    background: transparent;
    font-family: 'Poppins', sans-serif;
    color: white;
  }

  #app-container {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 300px;
    gap: 24px;
    max-width: 420px;
    margin: 0 auto;
    padding: 20px;
  }

  #labels {
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    height: 250px;
    width: 50px;
    font-size: 0.85rem;
  }

  .label {
    text-align: right;
    color: white;
  }

  #meter-wrapper {
    position: relative;
    width: 40px;
    height: 250px;
    background: linear-gradient(to top, #10b981, #facc15, #ef4444);
    border: 1px solid #444;
    border-radius: 12px;
    overflow: hidden;
    display: flex;
    align-items: flex-end;
  }

  #bar {
    width: 100%;
    height: 0%;
    background: rgba(0,0,0,0.4);
    border-radius: 12px 12px 0 0;
    transition: height 0.15s ease-out;
  }

  .tick-line {
    position: absolute;
    left: 100%;
    width: 10px;
    height: 1px;
    background: white;
    opacity: 0.3;
  }

  .tick-label {
    position: absolute;
    left: 120%;
    font-size: 0.7rem;
    color: white;
    opacity: 0.6;
  }

  #db-stats {
    display: flex;
    flex-direction: column;
    margin-left: 16px;
    gap: 4px;
  }

  #avg-db, #max-db {
    font-size: 0.9rem;
    color: #ccc;
  }

  #db-value {
    font-size: 1.1rem;
    font-weight: bold;
    color: white;
  }

  #reset-button {
    margin-top: 10px;
    font-size: 0.8rem;
    padding: 4px 12px;
    background: #e5e7eb;
    border: none;
    border-radius: 6px;
    cursor: pointer;
  }

  .overlay {
    position: absolute;
    top: 0; left: 0;
    width: 100%;
    height: 100%;
    backdrop-filter: blur(8px);
    display: flex;
    justify-content: center;
    align-items: center;
  }

  .overlay button {
    padding: 12px 24px;
    font-size: 1.1rem;
    background: #10b981;
    color: white;
    border: none;
    border-radius: 8px;
    cursor: pointer;
  }
</style>
</head>
<body>
  <div id="app-container">
    <div id="labels">
      <div class="label">130</div>
      <div class="label">120</div>
      <div class="label">110</div>
      <div class="label">100</div>
      <div class="label">90</div>
      <div class="label">80</div>
      <div class="label">70</div>
      <div class="label">60</div>
      <div class="label">50</div>
      <div class="label">40</div>
      <div class="label">30</div>
      <div class="label">20</div>
      <div class="label">10</div>
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

<script>
let dbHistory = [];
let maxDb = 0;
let lastDb = 0;
const smoothingFactor = 0.3;
const maxHistoryLength = 50;

function startApp() {
  document.getElementById("overlay").style.display = "none";
  initMic();
}

function initMic() {
  const bar = document.getElementById("bar");
  const dbValue = document.getElementById("db-value");
  const avgDbText = document.getElementById("avg-db");
  const maxDbText = document.getElementById("max-db");
  const resetButton = document.getElementById("reset-button");

  resetButton.onclick = () => {
    dbHistory = [];
    maxDb = 0;
    avgDbText.textContent = "Avg: 0 dB";
    maxDbText.textContent = "Max: 0 dB";
    dbValue.textContent = "dB: 0";
    bar.style.height = "0%";
  };

  navigator.mediaDevices.getUserMedia({ audio: true })
    .then(stream => {
      const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
      const source = audioCtx.createMediaStreamSource(stream);
      const analyser = audioCtx.createAnalyser();
      analyser.fftSize = 256;
      source.connect(analyser);
      const dataArray = new Uint8Array(analyser.fftSize);

      function updateMeter() {
        analyser.getByteTimeDomainData(dataArray);
        let sumSquares = 0;
        for (let i = 0; i < dataArray.length; i++) {
          const normalized = (dataArray[i] - 128) / 128;
          sumSquares += normalized * normalized;
        }
        const rms = Math.sqrt(sumSquares / dataArray.length);
        let db = 20 * Math.log10(rms + 1e-6);
        let positiveDb = Math.round((db + 100) * 1.2 + 10);

        const smoothedDb = smoothingFactor * lastDb + (1 - smoothingFactor) * positiveDb;
        lastDb = smoothedDb;

        dbHistory.push(smoothedDb);
        if (dbHistory.length > maxHistoryLength) dbHistory.shift();

        const avgDb = dbHistory.reduce((a, b) => a + b, 0) / dbHistory.length;
        maxDb = Math.max(maxDb, smoothedDb);

        const heightPercent = ((smoothedDb - 10) / 120) * 100;
        bar.style.height = heightPercent + "%";

        dbValue.textContent = `dB: ${Math.round(smoothedDb)}`;
        avgDbText.textContent = `Avg: ${Math.round(avgDb)} dB`;
        maxDbText.textContent = `Max: ${Math.round(maxDb)} dB`;
      }

      setInterval(updateMeter, 100);
    })
    .catch(err => {
      document.getElementById("overlay").innerHTML = `<div style='color:red; text-align:center;'>Microphone access denied.<br>Please allow microphone access and refresh.</div>`;
    });
}
</script>
</body>
</html>
"""

html(meter_html, height=460, scrolling=False)
