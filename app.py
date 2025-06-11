import streamlit as st
from streamlit.components.v1 import html

st.set_page_config(page_title="Mic dB Level", layout="centered")

st.markdown(
    """
    <style>
      .stApp {
        background-color: black !important;
        color: white !important;
      }
      .streamlit-title {
        font-size: 3em !important;
        font-weight: bold !important;
        color: white !important;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<h1 class="streamlit-title">Sound Level Meter</h1>', unsafe_allow_html=True)

meter_html = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<style>
  @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@600&display=swap');

  html, body {
    margin: 0; padding: 0;
    background: transparent;
    font-family: 'Poppins', sans-serif;
    color: white;
    user-select: none;
  }

  #app-container {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 320px;
    max-width: 440px;
    margin: 40px auto;
    position: relative;
  }

  #labels {
    position: relative;
    height: 280px;
    width: 60px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    font-size: 0.85rem;
    font-weight: 500;
  }

  .label-row {
    position: relative;
    display: flex;
    align-items: center;
  }

  .tick {
    width: 10px;
    height: 1px;
    background: white;
    margin-right: 6px;
  }

  .label-text {
    width: 30px;
    text-align: right;
  }

  .red { color: #ef4444; }
  .yellow { color: #facc15; }
  .green { color: #10b981; }

  #meter-wrapper {
    position: relative;
    width: 60px;
    height: 280px;
    border-radius: 14px;
    background: #1f2937;
    border: 2px solid #374151;
    margin: 0 20px;
    overflow: hidden;
    display: flex;
    align-items: flex-end;
    box-shadow: inset 0 0 10px rgba(0,0,0,0.6), 0 4px 12px rgba(0,0,0,0.4);
  }

  #bar {
    width: 100%;
    height: 0;
    background: linear-gradient(to top, #ef4444, #facc15, #10b981);
    box-shadow: 0 0 15px 4px rgba(255, 0, 0, 0.4);
    border-radius: 14px 14px 0 0;
    transition: height 0.2s ease-out;
  }

  #db-stats {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    justify-content: center;
  }

  #avg-db, #max-db {
    font-size: 0.9rem;
    color: #9ca3af;
  }

  #db-value {
    font-weight: 700;
    font-size: 1.1rem;
    color: white;
  }

  #out-message {
    color: #ef4444;
    font-weight: 600;
    margin-top: 15px;
    text-align: center;
  }

  .overlay {
    position: absolute;
    z-index: 10;
    top: 0; left: 0;
    width: 100%; height: 100%;
    backdrop-filter: blur(10px);
    background: rgba(0, 0, 0, 0.4);
    display: flex;
    justify-content: center;
    align-items: center;
    flex-direction: column;
  }

  .overlay button {
    padding: 10px 24px;
    font-size: 1.2rem;
    background: #10b981;
    color: white;
    border: none;
    border-radius: 8px;
    cursor: pointer;
  }

  .overlay button:hover {
    background: #059669;
  }

  #reset-button {
    margin-top: 10px;
    font-size: 0.8rem;
    padding: 4px 12px;
    background: #e5e7eb;
    border: none;
    border-radius: 6px;
    color: black;
    cursor: pointer;
  }
</style>
</head>
<body>
  <div id="app-container">
    <div id="labels">
      <!-- Labels + ticks row -->
      {% for v, c in [
        (130,'red'), (120,'red'), (110,'red'),
        (100,'yellow'), (90,'yellow'), (80,'yellow'),
        (70,'green'), (60,'green'), (50,'green'),
        (40,'green'), (30,'green'), (20,'green'), (10,'green')
      ] %}
      <div class="label-row">
        <div class="tick"></div>
        <div class="label-text {{c}}">{{v}}</div>
      </div>
      {% endfor %}
    </div>

    <div id="meter-wrapper"><div id="bar"></div></div>

    <div id="db-stats">
      <div id="avg-db">Avg: 0 dB</div>
      <div id="max-db">Max: 0 dB</div>
      <div id="db-value">dB: 0</div>
      <button id="reset-button">Reset</button>
    </div>

    <div class="overlay" id="overlay">
      <button onclick="startApp()">Start</button>
    </div>
  </div>

  <div id="out-message"></div>

  <script>
    let lastDb = 0, dbHistory = [], intervalId;
    const smoothing = 0.3, historyMax = 50;

    function startApp() {
      document.getElementById('overlay').style.display = 'none';
      initMic();
    }

    function initMic() {
      const out = document.getElementById('out-message');
      const bar = document.getElementById('bar');
      const dbV = document.getElementById('db-value');
      const avgV = document.getElementById('avg-db');
      const maxV = document.getElementById('max-db');
      const reset = document.getElementById('reset-button');
      let maxDb = 0;

      reset.onclick = () => {
        dbHistory = []; lastDb = 0; maxDb = 0;
        bar.style.height = '0%';
        dbV.textContent = 'dB: 0';
        avgV.textContent = 'Avg: 0 dB';
        maxV.textContent = 'Max: 0 dB';
      };

      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        out.textContent = 'Microphone not supported.';
        return;
      }

      navigator.mediaDevices.getUserMedia({audio: true})
        .then(stream => {
          const ctx = new (AudioContext || webkitAudioContext)();
          const src = ctx.createMediaStreamSource(stream);
          const analyzer = ctx.createAnalyser();
          analyzer.fftSize = 256;
          src.connect(analyzer);
          const data = new Uint8Array(analyzer.fftSize);

          function update() {
            analyzer.getByteTimeDomainData(data);
            let sum=0;
            data.forEach(v => {
              const n = (v - 128)/128;
              sum += n*n;
            });
            const rms = Math.sqrt(sum/data.length);
            let db = 20 * Math.log10(rms + 1e-6);
            db = Math.max(-130, db);
            const pos = db + 130;

            const smooth = smoothing * lastDb + (1 - smoothing) * pos;
            lastDb = smooth;

            dbHistory.push(smooth);
            if (dbHistory.length > historyMax) dbHistory.shift();
            const avg = dbHistory.reduce((a,b)=>a+b)/dbHistory.length;
            maxDb = Math.max(maxDb, smooth);

            const pct = Math.min(100, (smooth / 130) * 100);
            bar.style.height = pct + '%';

            dbV.textContent = 'dB: ' + Math.round(smooth);
            avgV.textContent = 'Avg: ' + Math.round(avg) + ' dB';
            maxV.textContent = 'Max: ' + Math.round(maxDb) + ' dB';
          }

          update();
          intervalId = setInterval(update, 100);
          window.addEventListener('beforeunload', () => {
            clearInterval(intervalId);
            if (ctx.state !== 'closed') ctx.close();
          });
        })
        .catch(err => {
          out.textContent = 'Microphone access denied.';
          console.error(err);
        });
    }
  </script>
</body>
</html>
"""

html(meter_html.replace('{%','<!--').replace('%}','-->'), height=560, scrolling=False)
