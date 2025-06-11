import streamlit as st
from streamlit.components.v1 import html

st.set_page_config(page_title="Sound Level Meter", layout="centered")

st.markdown(
    """
    <style>
      .stApp {
        background-color: black;
        color: white;
      }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown("<h1 style='text-align:center; color:white;'>Sound Level Meter</h1>", unsafe_allow_html=True)

meter_html = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<style>
  body {
    background: transparent;
    color: white;
    font-family: Arial, sans-serif;
    user-select: none;
  }

  #app-container {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 320px;
    max-width: 500px;
    margin: 40px auto;
    position: relative;
  }

  #labels {
    height: 280px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    margin-right: 10px;
  }

  .label-row {
    display: flex;
    align-items: center;
    font-size: 0.8rem;
  }

  .tick {
    width: 8px;
    height: 1px;
    background: white;
    margin-right: 6px;
  }

  #meter-wrapper {
    position: relative;
    width: 50px;
    height: 280px;
    background: #1f2937;
    border-radius: 12px;
    border: 2px solid #374151;
    overflow: hidden;
    display: flex;
    align-items: flex-end;
  }

  #bar {
    width: 100%;
    height: 0;
    background: linear-gradient(to top, red, yellow, green);
    transition: height 0.1s ease-out;
    border-radius: 0 0 12px 12px;
  }

  #db-stats {
    margin-left: 20px;
    font-size: 0.9rem;
  }

  #db-stats div {
    margin-bottom: 8px;
  }

  button {
    padding: 6px 12px;
    margin-top: 10px;
    background: #10b981;
    color: white;
    border: none;
    border-radius: 6px;
    cursor: pointer;
  }

  #out-message {
    text-align: center;
    margin-top: 10px;
    color: #ef4444;
  }
</style>
</head>
<body>
<div id="app-container">
  <div id="labels">
    <div class="label-row"><div class="tick"></div><div>130</div></div>
    <div class="label-row"><div class="tick"></div><div>120</div></div>
    <div class="label-row"><div class="tick"></div><div>110</div></div>
    <div class="label-row"><div class="tick"></div><div>100</div></div>
    <div class="label-row"><div class="tick"></div><div>90</div></div>
    <div class="label-row"><div class="tick"></div><div>80</div></div>
    <div class="label-row"><div class="tick"></div><div>70</div></div>
    <div class="label-row"><div class="tick"></div><div>60</div></div>
    <div class="label-row"><div class="tick"></div><div>50</div></div>
    <div class="label-row"><div class="tick"></div><div>40</div></div>
    <div class="label-row"><div class="tick"></div><div>30</div></div>
    <div class="label-row"><div class="tick"></div><div>20</div></div>
    <div class="label-row"><div class="tick"></div><div>10</div></div>
  </div>

  <div id="meter-wrapper">
    <div id="bar"></div>
  </div>

  <div id="db-stats">
    <div id="avg-db">Avg: 0 dB</div>
    <div id="max-db">Max: 0 dB</div>
    <div id="db-value">dB: 0</div>
    <button onclick="resetMeter()">Reset</button>
  </div>
</div>
<div id="out-message"></div>

<script>
  let lastDb = 0, dbHistory = [], maxDb = 0;
  const smoothing = 0.3;

  function resetMeter() {
    dbHistory = [];
    maxDb = 0;
    document.getElementById("bar").style.height = "0%";
    document.getElementById("db-value").textContent = "dB: 0";
    document.getElementById("avg-db").textContent = "Avg: 0 dB";
    document.getElementById("max-db").textContent = "Max: 0 dB";
  }

  if (navigator.mediaDevices.getUserMedia) {
    navigator.mediaDevices.getUserMedia({audio: true}).then(function(stream) {
      const audioCtx = new AudioContext();
      const source = audioCtx.createMediaStreamSource(stream);
      const analyser = audioCtx.createAnalyser();
      analyser.fftSize = 256;
      source.connect(analyser);
      const data = new Uint8Array(analyser.fftSize);

      setInterval(() => {
        analyser.getByteTimeDomainData(data);
        let sum = 0;
        for (let i = 0; i < data.length; i++) {
          const normalized = (data[i] - 128) / 128;
          sum += normalized * normalized;
        }
        const rms = Math.sqrt(sum / data.length);
        let db = 20 * Math.log10(rms + 1e-6) + 130;
        db = Math.max(0, Math.min(130, db));

        const smoothDb = smoothing * lastDb + (1 - smoothing) * db;
        lastDb = smoothDb;
        dbHistory.push(smoothDb);
        if (dbHistory.length > 50) dbHistory.shift();
        const avg = dbHistory.reduce((a,b) => a+b, 0) / dbHistory.length;
        maxDb = Math.max(maxDb, smoothDb);

        const heightPct = (smoothDb / 130) * 100;
        document.getElementById("bar").style.height = heightPct + "%";

        document.getElementById("db-value").textContent = "dB: " + Math.round(smoothDb);
        document.getElementById("avg-db").textContent = "Avg: " + Math.round(avg) + " dB";
        document.getElementById("max-db").textContent = "Max: " + Math.round(maxDb) + " dB";
      }, 100);
    }).catch(function(err) {
      document.getElementById("out-message").textContent = "Microphone access denied.";
    });
  } else {
    document.getElementById("out-message").textContent = "Microphone not supported.";
  }
</script>
</body>
</html>
"""

html(meter_html, height=560, scrolling=False)
