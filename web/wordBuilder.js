let currentWord = '';
let lastLetter = null;
let holdStartTime = null;
const HOLD_DURATION = 1500; // milliseconds
const CONFIDENCE_THRESHOLD = 0.7;

function processLetter(result) {
  // result is { letter, confidence } from classifyLandmarks()
  // or null if no hand detected or model not ready

  if (!result || result.confidence < CONFIDENCE_THRESHOLD) {
    // No confident prediction — reset hold timer
    lastLetter = null;
    holdStartTime = null;
    updatePredictionDisplay(null);
    return;
  }

  const { letter, confidence } = result;

  // Always show the current prediction
  updatePredictionDisplay(result);

  // Check if this is the same letter as last frame
  if (letter !== lastLetter) {
    // Letter changed — start tracking this new letter
    lastLetter = letter;
    holdStartTime = Date.now();
    return;
  }

  // Same letter — check if hold duration has been reached
  const elapsed = Date.now() - holdStartTime;
  if (elapsed >= HOLD_DURATION) {
    appendLetter(letter);
    // Reset so the same letter doesn't keep appending
    holdStartTime = Date.now();
  }
}

function appendLetter(letter) {
  // NG detection logic
  // If last appended letter was N and current is G, replace N with NG
  if (letter === 'G' && currentWord.endsWith('N')) {
    currentWord = currentWord.slice(0, -1) + 'NG';
  } else {
    currentWord += letter;
  }

  updateWordDisplay();
}

function updatePredictionDisplay(result) {
  const letterEl = document.getElementById('predicted-letter');
  const confEl = document.getElementById('confidence-display');

  // Always remove previous highlight
  document.querySelectorAll('.fsl-item').forEach(el => el.classList.remove('active'));

  if (!result) {
    letterEl.textContent = '—';
    confEl.textContent = '';
    return;
  }

  letterEl.textContent = result.letter;
  confEl.textContent = (result.confidence * 100).toFixed(1) + '%';

  // Highlight the predicted letter in the sidebar
  const refEl = document.getElementById(`ref-${result.letter}`);
  if (refEl) refEl.classList.add('active');
}

function updateWordDisplay() {
  document.getElementById('current-word').textContent = currentWord;
}

function clearWord() {
  currentWord = '';
  lastLetter = null;
  holdStartTime = null;
  updateWordDisplay();
}

function speakWord() {
  if (!currentWord) return;
  const utterance = new SpeechSynthesisUtterance(currentWord);
  utterance.rate = 0.6
  window.speechSynthesis.speak(utterance);
}