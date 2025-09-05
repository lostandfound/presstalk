async function fetchConfig() {
  const res = await fetch('/api/config');
  if (!res.ok) throw new Error('Failed to load config');
  return await res.json();
}

async function postConfig(cfg) {
  const res = await fetch('/api/config', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(cfg),
  });
  return await res.json();
}

function fillForm(cfg) {
  document.getElementById('hotkey').value = cfg.hotkey || '';
  document.getElementById('language').value = cfg.language || 'ja';
  document.getElementById('model').value = cfg.model || 'small';
  document.getElementById('audio_feedback').checked = !!cfg.audio_feedback;
}

function readForm() {
  return {
    hotkey: document.getElementById('hotkey').value.trim(),
    language: document.getElementById('language').value,
    model: document.getElementById('model').value,
    audio_feedback: document.getElementById('audio_feedback').checked,
  };
}

function status(msg, ok = true) {
  const el = document.getElementById('status');
  el.textContent = msg || '';
  el.style.color = ok ? 'inherit' : 'crimson';
}

window.addEventListener('DOMContentLoaded', async () => {
  const form = document.getElementById('cfg-form');
  const resetBtn = document.getElementById('reset');
  try {
    const cfg = await fetchConfig();
    fillForm(cfg);
  } catch (e) {
    status('Failed to load configuration', false);
  }
  form.addEventListener('submit', async (ev) => {
    ev.preventDefault();
    status('Saving...');
    try {
      const result = await postConfig(readForm());
      if (result && result.ok) {
        status('Saved!');
      } else {
        status(result && result.error ? result.error : 'Save failed', false);
      }
    } catch (e) {
      status('Save failed', false);
    }
  });
  resetBtn.addEventListener('click', async () => {
    try {
      const cfg = await fetchConfig();
      fillForm(cfg);
      status('Reset to current values');
    } catch (e) {
      status('Failed to reload configuration', false);
    }
  });
});

