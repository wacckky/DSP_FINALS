import streamlit as st
from streamlit.components.v1 import html

st.set_page_config(page_title="Mic dB Level", layout="centered")

# Custom CSS for background and title
st.markdown(
    """
    <style>
    .stApp {
        background-image: url("https://raw.githubusercontent.com/wacckky/DSP_FINALS/main/DSP(1).jpg");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
        background-position: center;
        color: white !important;
    }

    .streamlit-title {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif !important;
        font-weight: 700 !important;
        font-size: 5em !important;
        color: white !important;
        text-shadow: 2px 2px 8px #000;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Title
st.markdown('<h1 class="streamlit-title">SOUND LEVEL METER</h1>', unsafe_allow_html=True)

# HTML + JS Meter
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
    justify-content: flex-start;
    align-items: center;
    height: 550px;
    max-width: 400px;
    margin: 35px auto 0;
    position: relative;
  }
  #labels {
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    height: 500px;
    width: 60px;
    font-size: 0.875rem;
    font-weight: 500;
  }
  .label {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    gap: 6px;
    color: white;
  }
  .tick {
    width: 10px;
    height: 2px;
    background-color: #9ca3af;
    margin-right: -15px;
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
    margin: 0 20px;
    display: flex;
    align-items: flex-end;
    box-shadow: inset 0 0 10px rgba(0,0,0,0.6), 0 4px 12px rgba(0,0,0,0.4);
  }
  #bar {
    width: 100%;
    height: 0%;
    border-radius: 14px 14px 0 0;
    background: linear-gradient(to top, #10b981, #facc15, #ef4444);
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
    font-size: 1.9rem;
    color: #9ca3af;
  }
  #db-value {
    font-weight: 700;
    font-size: 2.1rem;
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
  #reset-button, #pause-button {
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
      <div class="label red">130<span class="tick"></span></div>
      <div class="label red">120<span class="tick"></span></div>
      <div class="label red">110<span class="tick"></span></div>
      <div class="label yellow">100<span class="tick"></span></div>
      <div class="label yellow">90<span class="tick"></span></div>
      <div class="label yellow">80<span class="tick"></span></div>
      <div class="label green">70<span class="tick"></span></div>
      <div class="label green">60<span class="tick"></span></div>
      <div class="label green">50<span class="tick"></span></div>
      <div class="label green">40<span class="tick"></span></div>
      <div class="label green">30<span class="tick"></span></div>
      <div class="label green">20<span class="tick"></span></div>
      <div class="label green">10<span class="tick"></span></div>
    </div>

    <div id="meter-wrapper">
      <div id="bar"></div>
    </div>

    <div id="db-stats">
      <div id="avg-db">Avg: 0 dB</div>
      <div id="max-db">Max: 0 dB</div>
      <div id="db-value">dB: 0</div>
      <button id="reset-button">Reset</button>
      <button id="pause-button">Pause</button>
    </div>

    <div class="overlay" id="overlay">
      <button onclick="startApp()">Start</button>
    </div>
  </div>
  <div id="out-message"></div>

<script>
let lastDb = 0;
let dbHistory = [];
const smoothingFactor = 0.3;
const maxHistoryLength = 50;
let intervalId = null;
let isPaused = false;

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
  const pauseButton = document.getElementById("pause-button");

  let maxDb = 0;

  resetButton.onclick = () => {
    dbHistory = [];
    lastDb = 0;
    maxDb = 0;
    bar.style.height = "0%";
    dbValue.textContent = "dB: 0";
    avgDbText.textContent = "Avg: 0 dB";
    maxDbText.textContent = "Max: 0 dB";
  };

  pauseButton.onclick = () => {
    isPaused = !isPaused;
    pauseButton.textContent = isPaused ? "Resume" : "Pause";
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
        if (isPaused) return;

        analyser.getByteTimeDomainData(dataArray);
        let sumSquares = 0;
        for (let i = 0; i < dataArray.length; i++) {
          const normalized = (dataArray[i] - 128) / 128;
          sumSquares += normalized * normalized;
        }
        const rms = Math.sqrt(sumSquares / dataArray.length);
        const reference = 0.05;
        let db = 20 * Math.log10(rms / reference + 1e-15);
        let positiveDb = Math.max(0, Math.min(130, db + 20));


        const smoothedDb = smoothingFactor * lastDb + (1 - smoothingFactor) * positiveDb;
        lastDb = smoothedDb;

        dbHistory.push(smoothedDb);
        if (dbHistory.length > maxHistoryLength) dbHistory.shift();

        const avgDb = dbHistory.reduce((a, b) => a + b, 0) / dbHistory.length;
        maxDb = Math.max(maxDb, smoothedDb);
        const percentage = Math.min(100, (smoothedDb / 130) * 100);

        bar.style.height = percentage + "%";
        dbValue.textContent = `dB: ${Math.round(smoothedDb)}`;
        avgDbText.textContent = `Avg: ${Math.round(avgDb)} dB`;
        maxDbText.textContent = `Max: ${Math.round(maxDb)} dB`;
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

# Render in Streamlit
html(meter_html, height=650, scrolling=False)
