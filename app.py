import streamlit as st
from streamlit.components.v1 import html

st.set_page_config(page_title="Mic dB Level", layout="centered")
st.title("🎤 Live Microphone dB Meter")
st.write("This uses your **browser mic**. Grant permission when prompted.")

transparent_meter_html = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <title>Live Mic dB Meter</title>
  <style>
    html, body {
      margin: 0;
      padding: 0;
      background: transparent;
      overflow: hidden;
      font-family: Arial, sans-serif;
    }
    #out {
      font-size: 1.8rem;
      margin-bottom: 1rem;
      color: #333;
    }
    #bar-container {
      width: 30px;
      height: 250px;
      background: #ddd;
      border-radius: 15px;
      overflow: hidden;
      margin: 0 auto;
      position: relative;
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
  </style>
</head>
<body>
  <div id="out">dB: 0.00</div>
  <div id="bar-container">
    <div id="bar"></div>
  </div>

  <script>
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
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
            for (let i = 0; i < dataArray.length; i++) {
              let v = (dataArray[i] - 128) / 128;
              sum += v * v;
            }
            const rms = Math.sqrt(sum / dataArray.length);
            const db = 20 * Math.log10(rms + 1e-6);
            document.getElementById("out").innerText = `dB: ${db.toFixed(2)}`;

            // Map dB (roughly -100…0) to 0…100% height
            let pct = ((db + 100) / 100) * 100;
            pct = Math.max(0, Math.min(100, pct));
            document.getElementById("bar").style.height = pct + "%";
          }

          setInterval(updateMeter, 200);
        })
        .catch(err => {
          document.getElementById("out").innerText = "Mic access denied or unavailable";
          console.error("getUserMedia error:", err);
        });
    }
  </script>
</body>
</html>
"""

html(transparent_meter_html, height=350, scrolling=False)
