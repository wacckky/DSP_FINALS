import streamlit as st
from streamlit.components.v1 import html

st.set_page_config(page_title="Sound Level Meter", layout="centered")

st.title("🎤 Live Microphone dB Meter")
st.write("Please allow microphone access when prompted.")

meter_html = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Sound Level Meter</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@500&display=swap');

    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }

    html, body {
      height: 100%;
      background: linear-gradient(135deg, #c9d6ff, #e2e2e2);
      font-family: 'Poppins', sans-serif;
      display: flex;
      align-items: center;
      justify-content: center;
      overflow: hidden;
    }

    .glass-container {
      background: rgba(255, 255, 255, 0.15);
      border-radius: 20px;
      box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.2);
      backdrop-filter: blur(14px);
      -webkit-backdrop-filter: blur(14px);
      border: 1px solid rgba(255, 255, 255, 0.18);
      padding: 30px;
      width: 350px;
      text-align: center;
    }

    .title {
      font-size: 20px;
      margin-bottom: 20px;
      color: #ffffff;
      text-shadow: 0 1px 2px rgba(0,0,0,0.2);
    }

    .meter-wrapper {
      height: 250px;
      width: 40px;
      background: rgba(255, 255, 255, 0.1);
      border-radius: 16px;
      margin: 0 auto;
      overflow: hidden;
      position: relative;
      border: 2px solid rgba(255, 255, 255, 0.2);
    }

    .bar {
      position: absolute;
      bottom: 0;
      width: 100%;
      height: 0%;
      background: linear-gradient(to top, #22c55e, #facc15, #ef4444);
      transition: height 0.3s ease-in-out;
      border-radius: 16px 16px 0 0;
    }

    .ticks {
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      height: 250px;
      position: absolute;
      left: -40px;
      top: 0;
      font-size: 12px;
      color: white;
    }

    .tick {
      color: #ffffff88;
    }

    .tick.high { color: #ef4444; }
    .tick.mid { color: #facc15; }
    .tick.low { color: #22c55e; }

    .db-display {
      margin-top: 20px;
      color: white;
      font-weight: 600;
      font-size: 16px;
    }

    .reset-btn {
      margin-top: 20px;
      padding: 8px 18px;
      border-radius: 25px;
      border: none;
      font-size: 14px;
      background: linear-gradient(135deg, #6ee7b7, #3b82f6);
      color: white;
      cursor: pointer;
      box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
      transition: transform 0.2s ease;
    }

    .reset-btn:hover {
      transform: scale(1.05);
    }

    .error-message {
      color: #ff6b6b;
      font-weight: bold;
      margin-top: 10px;
    }
  </style>
</head>
<body>
  <div class="glass-container">
    <div class="title">🎤 Sound Level Meter</div>
    <div style="position: relative;">
      <div class="ticks">
        <div class="tick high">0 dB</div>
        <div class="tick high">-10</div>
        <div class="tick mid">-30</div>
        <div class="tick mid">-50</div>
        <div class="tick low">-70</div>
        <div class="tick low">-90</div>
        <div class="tick low">-100</div>
      </div>
      <div class="meter-wrapper">
        <div class="bar" id="bar"></div>
      </div>
    </div>
    <div class="db-display" id="db-display">dB: 0 | Avg: 0 | Max: 0</div>
    <button class="reset-btn" onclick="resetStats()">Reset</button>
    <div class="error-message" id="error-message"></div>
  </div>

  <script>
    let dbMax = -100;
    let dbSum = 0;
    let dbCount = 0;

    const bar = document.getElementById("bar");
    const dbDisplay = document.getElementById("db-display");
    const errorMessage = document.getElementById("error-message");

    function resetStats() {
      dbMax = -100;
      dbSum = 0;
      dbCount = 0;
    }

    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
      navigator.mediaDevices.getUserMedia({ audio: true })
        .then(stream => {
          const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
          const source = audioCtx.createMediaStreamSource(stream);
          const analyser = audioCtx.createAnalyser();
          analyser.fftSize = 2048;
          const dataArray = new Uint8Array(analyser.fftSize);
          source.connect(analyser);

          function animate() {
            analyser.getByteTimeDomainData(dataArray);
            let sumSquares = 0;
            for (let i = 0; i < dataArray.length; i++) {
              const val = (dataArray[i] - 128) / 128;
              sumSquares += val * val;
            }
            const rms = Math.sqrt(sumSquares / dataArray.length);
            let db = 20 * Math.log10(rms + 1e-6);
            db = Math.max(-100, Math.min(0, db));
            const percent = ((db + 100) / 100) * 100;

            // Update stats
            dbMax = Math.max(dbMax, db);
            dbSum += db;
            dbCount++;

            const cur = Math.round(db);
            const avg = Math.round(dbSum / dbCount);
            const max = Math.round(dbMax);

            bar.style.height = `${percent}%`;
            dbDisplay.textContent = `dB: ${cur} | Avg: ${avg} | Max: ${max}`;

            requestAnimationFrame(animate);
          }

          animate();
        })
        .catch(err => {
          errorMessage.textContent = "Microphone access denied.";
          console.error(err);
        });
    } else {
      errorMessage.textContent = "Microphone not supported in this browser.";
    }
  </script>
</body>
</html>
"""

html(meter_html, height=600, scrolling=False)
