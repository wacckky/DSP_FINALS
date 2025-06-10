import streamlit as st
from streamlit.components.v1 import html

st.set_page_config(page_title="Mic dB Level", layout="centered")
st.title("Live Microphone dB Meter")
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

  /* Reset and base */
  html, body {
    margin: 0; padding: 0;
    background: transparent;
    font-family: 'Poppins', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen,
      Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
    color: #6b7280;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    height: 100%;
    user-select: none;
  }

  h1, h2, h3, h4, h5, h6 {
    color: #111827;
    font-weight: 600;
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
    position: relative;
  }

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

  #db-value {
    font-weight: 700;
    font-size: 1.1rem;
    color: #ffffff;
    min-width: 60px;
    text-align: left;
    user-select: none;
    align-self: flex-end;
    margin-left: 16px;
  }

  /* Accessibility */
  #out-message {
    color: #ef4444;
    font-weight: 600;
    margin-top: 15px;
    text-align: center;
  }

</style>
</head>
<body>
  <div id="app-container">
    <div id="labels" aria-label="dB scale labels" role="list">
      <div class="label" role="listitem">0</div>
      <div class="label" role="listitem">-10</div>
      <div class="label" role="listitem">-20</div>
      <div class="label" role="listitem">-30</div>
      <div class="label" role="listitem">-40</div>
      <div class="label" role="listitem">-50</div>
      <div class="label" role="listitem">-60</div>
      <div class="label" role="listitem">-70</div>
      <div class="label" role="listitem">-80</div>
      <div class="label" role="listitem">-90</div>
      <div class="label" role="listitem">-100</div>
    </div>
    <div id="meter-wrapper" aria-label="Microphone level meter">
      <div id="bar"></div>
    </div>
    <div id="db-value" aria-live="polite" aria-atomic="true">dB: 0.00</div>
  </div>
  <div id="out-message" role="alert" aria-live="assertive"></div>


  <script>
    (function () {
      const outMessage = document.getElementById('out-message');
      const bar = document.getElementById("bar");
      const dbValue = document.getElementById("db-value");

      // Initialize Audio context and stream
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

          function updateMeter() {
            analyser.getByteTimeDomainData(dataArray);
            let sumSquares = 0;
            for (let i = 0; i < dataArray.length; i++) {
              const normalized = (dataArray[i] - 128) / 128;
              sumSquares += normalized * normalized;
            }
            const rms = Math.sqrt(sumSquares / dataArray.length);
            const db = 20 * Math.log10(rms + 1e-6); // avoid log(0) by offset

            // Clamp dB between -100 and 0 for display
            const clampedDb = Math.min(0, Math.max(db, -100));

            // Map dB to percentage (0% at -100 dB, 100% at 0 dB)
            const percentage = ((clampedDb + 100) / 100) * 100;

            bar.style.height = percentage + "%";
            dbValue.textContent = `dB: ${clampedDb.toFixed(2)}`;
            outMessage.textContent = "";
          }

          updateMeter();
          const intervalId = setInterval(updateMeter, 100); // refresh every 100ms

          // Clean up on page unload - stop audio context
          window.addEventListener('beforeunload', () => {
            clearInterval(intervalId);
            if(audioCtx.state !== 'closed') audioCtx.close();
          });

        })
        .catch(err => {
          outMessage.textContent = "Microphone access denied.";
          console.error(err);
        });
    })();
  </script>
</body>
</html>
"""

html(meter_html, height=350, scrolling=False)

