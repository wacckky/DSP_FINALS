<!-- Streamlit App - Positive dB Meter (10 to 130 dB) -->

import streamlit as st
from streamlit.components.v1 import html

st.set_page_config(page_title="Mic dB Level", layout="centered")

# Inject CSS to set background color and title style
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
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Live Mic dB Meter</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@600&display=swap');

  html, body {
    margin: 0; padding: 0;
    background: transparent;
    font-family: 'Poppins', sans-serif;
    height: 100%;
    user-select: none;
    color: white;
  }

  #app-container {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 280px;
    gap: 24px;
    max-width: 400px;
    margin: 0 auto;
    padding: 20px;
    position: relative;
  }

  #labels {
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    height: 250px;
    width: 40px;
    font-size: 0.875rem;
    font-weight: 500;
  }

  .label {
    text-align: right;
    color: white;
  }

  .red { color: #ef4444; }
  .yellow { color: #facc15; }
  .green { color: #10b981; }

  #meter-wrapper {
    position: relative;
    width: 40px;
    height: 250px;
    border-radius: 12px;
    box-shadow: 0 0 8px rgba(0,0,0,0.08);
    border: 1.5px solid #e5e7eb;
    background: #f9fafb;
    overflow: hidden;
    display: flex;
    align-items: flex-end;
  }

  #bar {
    width: 100%;
    height: 0%;
    background: linear-gradient(to top, #10b981, #facc15, #ef4444);
    border-radius: 12px 12px 0 0;
    transition: height 0.2s ease-out;
    box-shadow: 0 4px 10px -1px rgba(255, 70, 70, 0.6);
  }

  #db-stats {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    justify-content: center;
    margin-left: 16px;
  }

  #avg-db, #max-db {
    font-size: 0.9rem;
    color: #6b7280;
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
    background: transparent;
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
  }
</style>
</head>
<body>
  <div id="app-container">
    <div id="labels">
      <div class="label red">130</div>
      <div class="label red">120</div>
      <div class="label red">110</div>
      <div class="label yellow">100</div>
      <div class="label yellow">90</div>
      <div class="label yellow">80</div>
      <div class="label green">70</div>
      <div class="label green">50</div>
      <div class="label green">30</div>
      <div class="label green">20</div>
      <div class="label green">10</div>
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
let lastDb = -100;
let dbHistory = [];
const smoothingFactor = 0.3;
const maxHistoryLength = 50;
let intervalId = null;

function startApp() {
  document.getElementById("overlay").style.display = "none";
  initMic();
}

function initMic() {
  const outMessage = document.getElementById('out-message');
  const bar = document.getElementById("bar");
  const dbValue = document.getElementById("db-value");
  const avgDbText = document.getElementById("avg-db");
  const maxDbText = document.getElementById("max-db");
  const resetButton = document.getElementById("reset-button");

  let maxDb = -100;

  resetButton.onclick = () => {
    dbHistory = [];
    maxDb = -100;
    avgDbText.textContent = "Avg: 0 dB";
    maxDbText.textContent = "Max: 0 dB";
  };

  if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
    outMessage.textContent = "getUserMedia not supported by your browser.";
    return;
  }

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
        db = Math.min(0, Math.max(db, -100));

        const smoothedDb = smoothingFactor * lastDb + (1 - smoothingFactor) * db;
        lastDb = smoothedDb;

        dbHistory.push(smoothedDb);
        if (dbHistory.length > maxHistoryLength) dbHistory.shift();

        const avgDb = dbHistory.reduce((a, b) => a + b, 0) / dbHistory.length;
        maxDb = Math.max(maxDb, smoothedDb);

        const positiveDb = smoothedDb + 130;
        const avgPositiveDb = avgDb + 130;
        const maxPositiveDb = maxDb + 130;

        const percentage = ((positiveDb - 10) / 120) * 100; // scale from 10 to 130

        bar.style.height = percentage + "%";
        dbValue.textContent = `dB: ${Math.round(positiveDb)}`;
        avgDbText.textContent = `Avg: ${Math.round(avgPositiveDb)} dB`;
        maxDbText.textContent = `Max: ${Math.round(maxPositiveDb)} dB`;
      }

      updateMeter();
      intervalId = setInterval(updateMeter, 100);

      window.addEventListener('beforeunload', () => {
        clearInterval(intervalId);
        if (audioCtx.state !== 'closed') audioCtx.close();
      });

    })
    .catch(err => {
      outMessage.textContent = "Microphone access denied.";
      console.error(err);
    });
}
</script>
</body>
</html>
"""

html(meter_html, height=420, scrolling=False)
