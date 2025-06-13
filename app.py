import streamlit as st
from streamlit.components.v1 import html

st.set_page_config(page_title="Mic dB Level", layout="centered")

# Custom CSS
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

st.markdown('<h1 class="streamlit-title">SOUND LEVEL METER</h1>', unsafe_allow_html=True)

# SOUND METER HTML + JS
meter_html = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<style>
/* CSS omitted for brevity — keep your existing style block here */
</style>
</head>
<body>
<div id="app-container">
  <!-- ... (keep your labels, meter, buttons, and overlay) ... -->
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

        // dB without bias
        let db = 20 * Math.log10(rms + 1e-6);
        let positiveDb = Math.max(0, Math.min(130, db));

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

# Display in Streamlit
html(meter_html, height=650, scrolling=False)
