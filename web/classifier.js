let model = null;
let labelMap = null;

async function loadModel() {
  const response = await fetch('./label_map.json');
  labelMap = await response.json();

  model = await tf.loadLayersModel('./tfjs_model/model.json');
  console.log('Model and label map loaded');
}

function normalizeLandmarks(landmarks) {
  // Step 1 — Wrist normalization
  // Subtract landmark 0 (wrist) x and y from all landmarks
  // Z is kept as-is — it already represents depth relative to wrist
  const wristX = landmarks[0].x;
  const wristY = landmarks[0].y;

  const flat = [];
  for (let i = 0; i < landmarks.length; i++) {
    flat.push(landmarks[i].x - wristX);
    flat.push(landmarks[i].y - wristY);
    flat.push(landmarks[i].z);
  }

  // Step 2 — Scale normalization
  // Divide by max absolute value so hand size doesn't affect output
  const maxVal = Math.max(...flat.map(v => Math.abs(v)));
  const normalized = flat.map(v => v / maxVal);

  // Result is a flat 63-element array — Step 3 (flatten) is already done
  // because we built it flat from the start
  return normalized;
}

function classifyLandmarks(landmarks) {
  if (!model || !labelMap) return null;

  const normalized = normalizeLandmarks(landmarks);

  // Convert to tensor of shape [1, 63]
  const input = tf.tensor2d([normalized]);
  const prediction = model.predict(input);
  const probabilities = prediction.dataSync();

  // Find the class with highest probability
  let maxIndex = 0;
  let maxProb = 0;
  for (let i = 0; i < probabilities.length; i++) {
    if (probabilities[i] > maxProb) {
      maxProb = probabilities[i];
      maxIndex = i;
    }
  }

  // Clean up tensor to avoid memory leak
  input.dispose();
  prediction.dispose();

  return {
    letter: labelMap[maxIndex],
    confidence: maxProb
  };
}