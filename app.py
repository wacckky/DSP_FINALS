import streamlit as st
from streamlit.components.v1 import html

st.set_page_config(page_title="Mic dB Level", layout="centered")
st.title("🎤 Sound Level Meter")

# Streamlit slider for smoothing
smoothing_factor = st.slider("Smoothing Factor", min_value=0.0, max_value=1.0, value=0.3, step=0.05)

# Inject the slider value into JavaScript
meter_html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Live Mic dB Meter</title>
<!-- Styles here (unchanged) -->
<style>
  /* (All your CSS remains unchanged) */
</style>
</head>
<body>
  <!-- (All your HTML body content remains unchanged) -->

<script>
// Injected smoothing factor from Streamlit
let smoothingFactor = {smoothing_factor};
let lastDb = -100;
let dbHistory = [];
const maxHistoryLength = 50;
let intervalId = null;

function startApp() {{
  document.getElementById("overlay").style.display = "none";
  initMic();
}}

function initMic() {{
  const outMessage = document.getElementById('out-message');
  const bar = document.getElementById("bar");
  const dbValue = document.getElementById("db-value");
  const avgDbText = document.getElementById("avg-db");
  const maxDbText = document.getElementById("max-db");
  const resetButton = document.getElementById("reset-button");

  let maxDb = -100;

  resetButton.onclick = () => {{
    dbHistory = [];
    maxDb = -100;
    avgDbText.textContent = "Avg: 0 dB";
    maxDbText.textContent = "Max: 0 dB";
  }};

  if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {{
    outMessage.textContent = "getUserMedia not supported by your browser.";
    return;
  }}

  navigator.mediaDevices.getUserMedia({{ audio: true }})
    .then(stream => {{
      const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
      const source = audioCtx.createMediaStreamSource(stream);
      const analyser = audioCtx.createAnalyser();
      analyser.fftSize = 256;
      source.connect(analyser);
      const dataArray = new Uint8Array(analyser.fftSize);

      function updateMeter() {{
        analyser.getByteTimeDomainData(dataArray);
        let sumSquares = 0;
        for (let i = 0; i < dataArray.length; i++) {{
          const normalized = (dataArray[i] - 128) / 128;
          sumSquares += normalized * normalized;
        }}
        const rms = Math.sqrt(sumSquares / dataArray.length);
        let db = 20 * Math.log10(rms + 1e-6);
        db = Math.min(0, Math.max(db, -100));

        const smoothedDb = smoothingFactor * lastDb + (1 - smoothingFactor) * db;
        lastDb = smoothedDb;

        dbHistory.push(smoothedDb);
        if (dbHistory.length > maxHistoryLength) dbHistory.shift();

        const avgDb = dbHistory.reduce((a, b) => a + b, 0) / dbHistory.length;
        maxDb = Math.max(maxDb, smoothedDb);

        const percentage = ((smoothedDb + 100) / 100) * 100;

        bar.style.height = percentage + "%";
        dbValue.textContent = `dB: ${{Math.round(smoothedDb)}}`;
        avgDbText.textContent = `Avg: ${{Math.round(avgDb)}} dB`;
        maxDbText.textContent = `Max: ${{Math.round(maxDb)}} dB`;
      }}

      updateMeter();
      intervalId = setInterval(updateMeter, 100);

      window.addEventListener('beforeunload', () => {{
        clearInterval(intervalId);
        if (audioCtx.state !== 'closed') audioCtx.close();
      }});
    }})
    .catch(err => {{
      outMessage.textContent = "Microphone access denied.";
      console.error(err);
    }});
}}
</script>
</body>
</html>
"""

html(meter_html, height=420, scrolling=False)
