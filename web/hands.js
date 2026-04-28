const videoEl = document.getElementById('webcam');
const canvasEl = document.getElementById('overlay');
const canvasCtx = canvasEl.getContext('2d');

canvasEl.width = 640;
canvasEl.height = 480;

// ── Button wiring ──
document.getElementById('start-btn').addEventListener('click', async () => {
  // Hide landing, show app
  document.getElementById('landing-screen').classList.add('hidden');
  document.getElementById('app-screen').classList.remove('hidden');

  // Load model and label map
  await loadModel();

  // Initialize and start MediaPipe
  startMediaPipe();
});

document.getElementById('speak-btn').addEventListener('click', () => {
  speakWord();
});

document.getElementById('clear-btn').addEventListener('click', () => {
  clearWord();
});

// ── MediaPipe Setup ──
function startMediaPipe() {
  const hands = new Hands({
    locateFile: (file) => {
      return `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}`;
    }
  });

  hands.setOptions({
    maxNumHands: 1,
    modelComplexity: 1,
    minDetectionConfidence: 0.7,
    minTrackingConfidence: 0.5
  });

  hands.onResults(onResults);

  const camera = new Camera(videoEl, {
    onFrame: async () => {
      await hands.send({ image: videoEl });
    },
    width: 640,
    height: 480
  });

  camera.start();
}

// ── Per-frame callback ──
function onResults(results) {
  // Clear the canvas each frame
  canvasCtx.clearRect(0, 0, canvasEl.width, canvasEl.height);

  if (!results.multiHandLandmarks || results.multiHandLandmarks.length === 0) {
    // No hand detected — reset prediction display
    processLetter(null);
    return;
  }

  const landmarks = results.multiHandLandmarks[0];

  // Draw skeleton on canvas
  drawConnectors(canvasCtx, landmarks, HAND_CONNECTIONS, {
    color: '#00ff88',
    lineWidth: 2
  });
  drawLandmarks(canvasCtx, landmarks, {
    color: '#ff4444',
    lineWidth: 1,
    radius: 3
  });

  // Classify and process
  const result = classifyLandmarks(landmarks);
  processLetter(result);
}