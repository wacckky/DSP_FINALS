import streamlit as st
from streamlit.components.v1 import html

st.set_page_config(page_title="Mic dB Level", layout="centered")
st.title("🎤 Live Microphone dB Meter")
st.write("This uses your **browser mic**. Grant permission when prompted.")

mic_meter_html = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <title>Live Mic dB Meter</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      text-align: center;
      padding: 1rem;
      background: #f5f5f5;
    }
    h1 {
      margin-bottom: 0.5rem;
    }
    #out {
      font-size: 2rem;
      margin: 0.5rem 0;
    }
    #bar-container {
      width: 100%;
      height: 20px;
      background: #ddd;
      border-radius: 10px;
      overflow: hidden;
      margin-top: 0.5rem;
    }
    #bar {
      height: 100%;
      width: 0%;
      background: #4caf50;
      transition: width 0.15s ease-out;
    }
  </style>
</head>
<body>
  <h1>🎤 Live Microphone dB Meter</h1>
  <p>Allow microphone access when prompted.</p>
  <div id="out">dB: 0.00</div>
  <div id="bar-container"><div id="bar"></div></div>

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

            // Map dB (roughly -100…0) to 0…100% width
            let pct = ((db + 100) / 100) * 100;
            pct = Math.max(0, Math.min(100, pct));
            document.getElementById("bar").style.width = pct + "%";
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

# Render the inline HTML/JS
html(mic_meter_html, height=350, scrolling=True)
