import streamlit as st
from streamlit.components.v1 import html

st.set_page_config(page_title="Mic dB Level", layout="centered")
st.title("Sound Level Meter")
st.write("This uses your **browser mic**. Please grant microphone permission when prompted.")

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
    height: 100%;
    font-family: 'Poppins', sans-serif;
    background: #ffffff;
  }

  .container {
    position: relative;
    height: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
    filter: blur(0px);
    transition: filter 0.5s ease;
  }

  .overlay {
  position: absolute;
  z-index: 10;
  top: 0; left: 0;
  width: 100%;
  height: 100%;
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  background: transparent; /* keep background transparent */
  display: flex;
  justify-content: center;
  align-items: center;
  flex-direction: column;
}


  .overlay.hidden {
    display: none;
  }

  .start-button {
    background: #10b981;
    color: white;
    font-size: 1.5rem;
    padding: 16px 32px;
    border: none;
    border-radius: 12px;
    cursor: pointer;
    font-weight: bold;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
    transition: background 0.3s ease;
  }

  .start-button:hover {
    background: #059669;
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
  }

  #labels {
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    height: 250px;
    width: 40px;
    color: #9ca3af;
    font-size: 0.875rem;
    font-weight: 500;
    user-select: none;
  }

  .label {
    text-align: right;
  }

  #meter-wrapper {
    position: relative;
    width: 40px;
    height: 250px;
    border-radius: 12px;
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

  #db-value {
    font-weight: 700;
    font-size: 1.1rem;
    color: #111827;
    min-width: 60px;
    text-align: left;
    user-select: none;
    align-self: flex-end;
    margin-left: 16px;
  }

  #out-message {
    color: #ef4444;
    font-weight: 600;
    margin-top: 15px;
    text-align: center;
  }
</style>
</head>
<body>
  <div class="overlay" id="start-overlay">
    <button class="start-button" onclick="startApp()">Start</button>
  </div>

  <div class="container" id="app-container-blur">
    <div id="app-container">
      <div id="labels">
        <div class="label">0</div>
        <div class="label">-10</div>
        <div class="label">-20</div>
        <div class="label">-30</div>
        <div class="label">-40</div>
        <div class="label">-50</div>
        <div class="label">-60</div>
        <div class="label">-70</div>
        <div class="label">-80</div>
        <div class="label">-90</div>
        <div class="label">-100</div>
      </div>
      <div id="meter-wrapper">
        <div id="bar"></div>
      </div>
      <div id="db-value">dB: 0.00</div>
    </div>
  </div>
  <div id="out-message"></div>

  <script>
    function startApp() {
      document.getElementById('start-overlay').classList.add('hidden');
      document.getElementById('app-container-blur').style.filter = 'none';
      initMic();
    }

    function initMic() {
      const outMessage = document.getElementById('out-message');
      const bar = document.getElementById("bar");
      const dbValue = document.getElementById("db-value");

      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        outMessage.textContent = "getUserMedia not supported by your browser.";
        return;
      }

      navigator.mediaDevices.getUserMedia({ audio: true })
        .then(stream => {
          const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
          const source = audioCtx.createMediaStreamSource(stream);
          const analyser = audioCtx.createAnalyser();
          analyser.fftSize = 2048;
          source.connect(analyser);
          const dataArray = new Uint8Array(analyser.fftSize);

          let lastDb = -100;
          const smoothingFactor = 0.8;

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

            const percentage = ((smoothedDb + 100) / 100) * 100;
            bar.style.height = percentage + "%";
            dbValue.textContent = `dB: ${smoothedDb.toFixed(2)}`;
            outMessage.textContent = "";
          }

          updateMeter();
          const intervalId = setInterval(updateMeter, 100);

          window.addEventListener('beforeunload', () => {
            clearInterval(intervalId);
            if(audioCtx.state !== 'closed') audioCtx.close();
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
html(meter_html, height=350, scrolling=False)
