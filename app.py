import streamlit as st
from streamlit.components.v1 import html

st.set_page_config(page_title="Mic dB Level", layout="centered")
st.title("🎤 Live Microphone dB Meter")
st.write("This uses your **browser mic**. Grant permission when prompted.")

clean_labeled_meter_html = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <title>Labeled Mic dB Meter</title>
  <style>
    html, body {
      margin: 0;
      padding: 0;
      background: transparent !important;
      overflow: hidden;
      font-family: Arial, sans-serif;
    }

    #container {
      display: flex;
      justify-content: center;
      align-items: flex-end;
      gap: 10px;
      height: 280px;
      position: relative;
    }

    #labels {
      position: relative;
      height: 250px;
      width: 30px;
    }

   .label {
      position: absolute;
      left: 0;
      transform: translateY(50%);
      font-size: 0.75rem;
      color: #333;
    }

    .label:nth-child(1) { bottom:   0%; }   /* -100 dB */
    .label:nth-child(2) { bottom:  10%; }   /* -90 dB */
    .label:nth-child(3) { bottom:  20%; }   /* -80 dB */
    .label:nth-child(4) { bottom:  30%; }   /* -70 dB */
    .label:nth-child(5) { bottom:  40%; }   /* -60 dB */
    .label:nth-child(6) { bottom:  50%; }   /* -50 dB */
    .label:nth-child(7) { bottom:  60%; }   /* -40 dB */
    .label:nth-child(8) { bottom:  70%; }   /* -30 dB */
    .label:nth-child(9) { bottom:  80%; }   /* -20 dB */
    .label:nth-child(10) { bottom: 90%; }   /* -10 dB */
    .label:nth-child(11) { bottom: 100%; }  /*   0 dB */

    #bar-container {
      position: relative;
      width: 30px;
      height: 250px;
      border: 2px solid rgba(0, 0, 0, 0.2);
      border-radius: 15px;
      background: transparent;
      overflow: hidden;
    }

    #bar {
      width: 100%;
      height: 0%;
      background: linear-gradient(to top, green, yellow, red);
      position: absolute;
      bottom: 0;
      transition: height 0.15s ease-out;
      transform-origin: bottom;
    }

    #out {
      text-align: center;
      margin-top: -20px;
      font-size: 1rem;
      color: #333;
    }
  </style>
</head>
<body>
  <div id="out">dB: 0.00</div>
  <div id="container">
    <div id="labels">
      <div class="label">–100</div>
      <div class="label">–90</div>
      <div class="label">–80</div>
      <div class="label">–70</div>
      <div class="label">–60</div>
      <div class="label">–50</div>
      <div class="label">–40</div>
      <div class="label">–30</div>
      <div class="label">–20</div>
      <div class="label">–10</div>
      <div class="label">0</div>
    </div>
    <div id="bar-container">
      <div id="bar"></div>
    </div>
  </div>

  <script>
    if (!navigator.mediaDevices?.getUserMedia) {
      document.getElementById("out").innerText = "getUserMedia not supported";
    } else {
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
            let sum = 0;
            for (let v of dataArray) {
              const norm = (v - 128) / 128;
              sum += norm * norm;
            }
            const rms = Math.sqrt(sum / dataArray.length);
            const db = 20 * Math.log10(rms + 1e-6);
            document.getElementById("out").innerText = `dB: ${db.toFixed(2)}`;

            let pct = ((db + 100) / 100) * 100;
            pct = Math.max(0, Math.min(100, pct));
            document.getElementById("bar").style.height = pct + "%";
          }

          setInterval(updateMeter, 200);
        })
        .catch(err => {
          document.getElementById("out").innerText = "Mic access denied";
          console.error(err);
        });
    }
  </script>
</body>
</html>
"""

html(clean_labeled_meter_html, height=330, scrolling=False)
