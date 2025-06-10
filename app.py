import streamlit as st
from streamlit.components.v1 import html

st.set_page_config(page_title="Mic dB Level", layout="centered")
st.title("🔊 Sound Level Meter")

html_code = """
<!DOCTYPE html>
<html>
<head>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@600&display=swap');

    :root {
      --bg-color: #f9fafb;
      --text-color: #111827;
      --subtext-color: #6b7280;
      --border-color: #e5e7eb;
      --bar-gradient: linear-gradient(to top, #10b981, #facc15, #ef4444);
    }

    @media (prefers-color-scheme: dark) {
      :root {
        --bg-color: #1f2937;
        --text-color: #f9fafb;
        --subtext-color: #d1d5db;
        --border-color: #374151;
      }
    }

    html, body {
      margin: 0; padding: 0;
      background: transparent;
      font-family: 'Poppins', sans-serif;
      color: var(--text-color);
    }

    #container {
      display: flex;
      align-items: center;
      justify-content: center;
      flex-direction: column;
      height: 320px;
    }

    #meter {
      width: 40px;
      height: 200px;
      border: 2px solid var(--border-color);
      border-radius: 8px;
      overflow: hidden;
      background-color: var(--bg-color);
      margin-bottom: 10px;
      position: relative;
    }

    #bar {
      position: absolute;
      bottom: 0;
      width: 100%;
      height: 0%;
      background: var(--bar-gradient);
      transition: height 0.1s ease;
    }

    #stats {
      font-size: 16px;
      color: var(--subtext-color);
    }

    #db {
      font-weight: bold;
      font-size: 20px;
      color: var(--text-color);
    }

    .overlay {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      backdrop-filter: blur(8px);
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .overlay button {
      padding: 10px 20px;
      font-size: 18px;
      background: #10b981;
      color: white;
      border: none;
      border-radius: 6px;
      cursor: pointer;
    }
  </style>
</head>
<body>
  <div id="container">
    <div id="meter">
      <div id="bar"></div>
    </div>
    <div id="db">dB: 0</div>
    <div id="stats">Waiting for microphone input...</div>
    <div class="overlay" id="overlay">
      <button onclick="startMeter()">Start</button>
    </div>
  </div>

  <script>
    let bar = null;
    let dbText = null;
    let stats = null;

    function startMeter() {
      document.getElementById('overlay').style.display = 'none';
      bar = document.getElementById("bar");
      dbText = document.getElementById("db");
      stats = document.getElementById("stats");

      navigator.mediaDevices.getUserMedia({ audio: true })
        .then(function(stream) {
          const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
          const analyser = audioCtx.createAnalyser();
          analyser.fftSize = 256;

          const source = audioCtx.createMediaStreamSource(stream);
          source.connect(analyser);

          const dataArray = new Uint8Array(analyser.fftSize);

          function update() {
            analyser.getByteTimeDomainData(dataArray);

            let sum = 0;
            for (let i = 0; i < dataArray.length; i++) {
              let val = (dataArray[i] - 128) / 128;
              sum += val * val;
            }

            let rms = Math.sqrt(sum / dataArray.length);
            let db = 20 * Math.log10(rms + 1e-6);
            db = Math.max(-100, Math.min(0, db));

            let percent = (db + 100);
            bar.style.height = percent + "%";
            dbText.textContent = "dB: " + Math.round(db);
            stats.textContent = "Microphone active";
            requestAnimationFrame(update);
          }

          update();
        })
        .catch(function(err) {
          stats.textContent = "Microphone access denied.";
        });
    }
  </script>
</body>
</html>
"""

html(html_code, height=400)
