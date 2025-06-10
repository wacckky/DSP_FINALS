import streamlit as st
from streamlit.components.v1 import html

st.set_page_config(page_title="Mic dB Level", layout="centered")
st.title("🎤 Live Microphone dB Meter")
st.write("This uses your **browser mic**. Grant permission when prompted.")

detailed_ticks_html = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <title>Mic dB Meter with Ticks</title>
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
      height: 300px;
      position: relative;
    }

    #labels {
      position: relative;
      height: 250px;
      width: 35px;
    }

    .label {
      position: absolute;
      left: 0;
      transform: translateY(50%);
      font-size: 0.7rem;
      color: #333;
    }

    /* Generate 11 tick positions from 0 to -100 dB */
    %s

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
      %s
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

# Generate CSS + HTML ticks for -100 to 0 dB
label_blocks = []
css_blocks = []
for i in range(11):
    db = -100 + i * 10
    percent = i * 10  # from 0 to 100%
    label_id = f"label{i}"
    css_blocks.append(f".label:nth-child({i+1}) {{ bottom: {percent}%; }}")
    label_blocks.append(f'<div class="label">{db}</div>')

final_html = detailed_ticks_html % ("\n".join(css_blocks), "\n".join(label_blocks))

html(final_html, height=330, scrolling=False)
