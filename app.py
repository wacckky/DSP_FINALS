import streamlit as st
from streamlit.components.v1 import html

st.set_page_config(page_title="Mic dB Level", layout="centered")
st.title("🎤 Sound Level Meter")

# Streamlit slider for smoothing
smoothing_factor = st.slider("Smoothing Factor", min_value=0.0, max_value=1.0, value=0.3, step=0.05)

# HTML + JS Template
meter_html = f"""
<div id="smoothing-config" data-smoothing="{smoothing_factor}"></div>

<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <style>
    body {{
      font-family: sans-serif;
    }}
    #bar {{
      height: 0%;
      width: 40px;
      background: linear-gradient(to top, #10b981, #facc15, #ef4444);
      transition: height 0.2s ease-out;
      border-radius: 12px 12px 0 0;
    }}
    #meter {{
      width: 40px;
      height: 250px;
      background: #eee;
      border-radius: 12px;
      overflow: hidden;
    }}
  </style>
</head>
<body>
  <div style="display: flex; flex-direction: column; align-items: center;">
    <div id="meter">
      <div id="bar"></div>
    </div>
    <p id="dB-display">dB: 0</p>
  </div>

<script>
let smoothingFactor = parseFloat(parent.document.getElementById('smoothing-config')?.dataset?.smoothing || 0.3);
let lastDb = -100;
let dbHistory = [];
const maxHistoryLength = 50;

navigator.mediaDevices.getUserMedia({ audio: true }).then(stream => {{
  const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
  const source = audioCtx.createMediaStreamSource(stream);
  const analyser = audioCtx.createAnalyser();
  analyser.fftSize = 256;
  const dataArray = new Uint8Array(analyser.fftSize);
  source.connect(analyser);

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

    const percentage = ((smoothedDb + 100) / 100) * 100;
    document.getElementById("bar").style.height = percentage + "%";
    document.getElementById("dB-display").textContent = "dB: " + Math.round(smoothedDb);
  }}

  setInterval(updateMeter, 100);
}});
</script>
</body>
</html>
"""

html(meter_html, height=400)
