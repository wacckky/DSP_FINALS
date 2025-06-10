const streamlit = window.streamlit;

navigator.mediaDevices.getUserMedia({ audio: true }).then((stream) => {
  const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
  const source = audioCtx.createMediaStreamSource(stream);
  const analyser = audioCtx.createAnalyser();
  const dataArray = new Uint8Array(analyser.fftSize);
  source.connect(analyser);

  function getVolume() {
    analyser.getByteTimeDomainData(dataArray);
    let sum = 0;
    for (let i = 0; i < dataArray.length; i++) {
      let val = (dataArray[i] - 128) / 128;
      sum += val * val;
    }
    const rms = Math.sqrt(sum / dataArray.length);
    const db = 20 * Math.log10(rms + 1e-6); // avoid log(0)

    document.getElementById("output").innerText = `dB: ${db.toFixed(2)}`;
    streamlit.setComponentValue(db);
  }

  setInterval(getVolume, 200);
});
