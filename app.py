import streamlit as st
from streamlit.components.v1 import html

st.set_page_config(page_title="Sound Level Meter", layout="centered")

st.markdown('<h1 style="color:white;">Sound Level Meter</h1>', unsafe_allow_html=True)

html_code = """
<style>
body {
    background-color: black;
    color: white;
}

#app-container {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 550px;
    max-width: 650px;
    margin: 40px auto 0;
    font-family: 'Poppins', sans-serif;
}

#labels {
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    height: 500px;
    width: 30px;
    font-size: 0.875rem;
    font-weight: 500;
    margin-right: 5px;
    text-align: right;
}

#tick-lines {
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    height: 500px;
    width: 20px;
    margin-right: 4px;
}

.tick-line {
    height: 1px;
    width: 20px;
    background-color: #9ca3af;
    align-self: flex-end;
}

#meter-wrapper {
    position: relative;
    width: 50px;
    height: 500px;
    border-radius: 14px;
    background: #1f2937;
    border: 2px solid #374151;
    overflow: hidden;
    box-shadow: inset 0 0 10px rgba(0,0,0,0.6), 0 4px 12px rgba(0,0,0,0.4);
    display: flex;
    align-items: flex-end;
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
    margin-left: 20px;
    font-size: 0.9rem;
    color: #9ca3af;
}

#db-value {
    font-weight: 700;
    font-size: 1.1rem;
    color: #ffffff;
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

.overlay {
    position: absolute;
    z-index: 10;
    top: 0; left: 0;
    width: 100%;
    height: 100%;
    backdrop-filter: blur(10px);
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
}

.overlay button:hover {
    background: #059669;
}

.red { color: #ef4444; }
.yellow { color: #facc15; }
.green { color: #10b981; }
</style>

<div id="app-container">
  <div id="labels">
    <div class="label red">130</div>
    <div class="label red">120</div>
    <div class="label red">110</div>
    <div class="label yellow">100</div>
    <div class="label yellow">90</div>
    <div class="label yellow">80</div>
    <div class="label green">70</div>
    <div class="label green">60</div>
    <div class="label green">50</div>
    <div class="label green">40</div>
    <div class="label green">30</div>
    <div class="label green">20</div>
    <div class="label green">10</div>
  </div>

  <div id="tick-lines">
    <div class="tick-line"></div>
    <div class="tick-line"></div>
    <div class="tick-line"></div>
    <div class="tick-line"></div>
    <div class="tick-line"></div>
    <div class="tick-line"></div>
    <div class="tick-line"></div>
    <div class="tick-line"></div>
    <div class="tick-line"></div>
    <div class="tick-line"></div>
    <div class="tick-line"></div>
    <div class="tick-line"></div>
    <div class="tick-line"></div>
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
let lastDb = 0;
let dbHistory = [];
const smoothingFactor = 0.3;
const maxHistoryLength = 50;
let intervalId = null;

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

  let maxDb = 0;

  resetButton.onclick = () => {
    dbHistory = [];
    lastDb = 0;
    maxDb = 0;
    bar.style.transition = "height 0.3s ease-in-out";
    bar.style.height = "0%";
    dbValue.textContent = "dB: 0";
    avgDbText.textContent = "Avg: 0 dB";
    maxDbText.textContent = "Max: 0 dB";
  };

  if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
    alert("Microphone not supported.");
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
        db = Math.max(-130, db);
        let positiveDb = 130 + db;
        const smoothedDb = smoothingFactor * lastDb + (1 - smoothingFactor) * positiveDb * 0.85;
        lastDb = smoothedDb;

        dbHistory.push(smoothedDb);
        if (dbHistory.length > maxHistoryLength) dbHistory.shift();

        const avgDb = dbHistory.reduce((a, b) => a + b, 0) / dbHistory.length;
        maxDb = Math.max(maxDb, smoothedDb);
        const percentage = Math.min(100, (smoothedDb / 130) * 100);

        bar.style.transition = "height 0.15s ease-out";
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
      alert("Microphone access denied.");
      console.error(err);
    });
}
</script>
"""

html(html_code, height=650, scrolling=False)
