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

let _hkTimer = null;
async function validateHotkeyLive(value) {
  const err = document.getElementById('hotkey-error');
  const input = document.getElementById('hotkey');
  if (!err) return;
  if (!value) {
    err.textContent = '';
    err.classList.remove('error');
    if (input) input.setAttribute('aria-invalid', 'false');
    err.setAttribute('role', 'status');
    return;
  }
  try {
    const res = await fetch('/api/validate/hotkey', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ hotkey: value }),
    });
    const j = await res.json();
    if (j && j.ok) {
      if (j.valid) {
        err.textContent = 'OK: ' + (j.normalized || value);
        err.classList.remove('error');
        if (input) input.setAttribute('aria-invalid', 'false');
        err.setAttribute('role', 'status');
      } else {
        err.textContent = 'Invalid hotkey';
        err.classList.add('error');
        if (input) input.setAttribute('aria-invalid', 'true');
        err.setAttribute('role', 'alert');
      }
    }
  } catch {}
}

let _hkTimer = null;
async function validateHotkeyLive(value) {
  const err = document.getElementById('hotkey-error');
  if (!err) return;
  if (!value) {
    err.textContent = '';
    err.classList.remove('error');
    return;
  }
  try {
    const res = await fetch('/api/validate/hotkey', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ hotkey: value }),
    });
    const j = await res.json();
    if (j && j.ok) {
      if (j.valid) {
        err.textContent = 'OK: ' + (j.normalized || value);
        err.classList.remove('error');
      } else {
        err.textContent = 'Invalid hotkey';
        err.classList.add('error');
      }
    }
  } catch {}
}

async function beepPreview() {
  try {
    const res = await fetch('/api/beep', { method: 'POST' });
    const j = await res.json();
    if (!j.ok) throw new Error('beep failed');
  } catch {}
}

let _hkTesting = false;
let _hkHandler = null;
let _hkTesting = false;
let _hkHandler = null;
function startHotkeyTest() {
  if (_hkTesting) return;
  _hkTesting = true;
  const stopBtn = document.getElementById('stop-hotkey');
  const testBtn = document.getElementById('test-hotkey');
  const saveBtn = document.getElementById('save');
  if (stopBtn) stopBtn.classList.remove('hidden');
  if (testBtn) testBtn.disabled = true;
  if (testBtn) testBtn.setAttribute('aria-pressed', 'true');
  if (saveBtn) saveBtn.disabled = true;
  status('Testing... Press your key combo. Press Esc or Stop to exit.');
  function buildCombo(e) {
    const parts = [];
    if (e.metaKey) parts.push('cmd');
    if (e.ctrlKey) parts.push('ctrl');
    if (e.altKey) parts.push('alt');
    if (e.shiftKey) parts.push('shift');
    let k = e.key || '';
    if (k === ' ') k = 'space';
    k = (k || '').toLowerCase();
    // ignore modifiers if they are the only key and already captured
    if (!['shift','control','alt','meta'].includes(k)) {
      parts.push(k);
    }
    return parts.join('+');
  }
  function onKeyDown(e) {
    if (e.key === 'Escape') {
      stopHotkeyTest();
      return;
    }
    const combo = buildCombo(e);
    if (combo) {
      const inp = document.getElementById('hotkey');
      inp.value = combo;
      status('Captured: ' + combo);
      e.preventDefault();
      // trigger live validation display
      validateHotkeyLive(combo);
    }
  }
  _hkHandler = onKeyDown;
  window.addEventListener('keydown', _hkHandler, true);
}

function stopHotkeyTest() {
  if (!_hkTesting) return;
  _hkTesting = false;
  if (_hkHandler) {
    window.removeEventListener('keydown', _hkHandler, true);
    _hkHandler = null;
  }
  const stopBtn = document.getElementById('stop-hotkey');
  const testBtn = document.getElementById('test-hotkey');
  const saveBtn = document.getElementById('save');
  if (stopBtn) stopBtn.classList.add('hidden');
  if (testBtn) testBtn.disabled = false;
  if (testBtn) testBtn.setAttribute('aria-pressed', 'false');
  if (saveBtn) saveBtn.disabled = false;
  status('Hotkey capture stopped');
  setTimeout(() => status(''), 1000);
}

window.addEventListener('DOMContentLoaded', async () => {
  const form = document.getElementById('cfg-form');
  const saveBtn = document.getElementById('save');
  const resetBtn = document.getElementById('reset');
  const testBtn = document.getElementById('test-hotkey');
  const beepBtn = document.getElementById('beep');
  const stopBtn = document.getElementById('stop-hotkey');
  const hotkeyInput = document.getElementById('hotkey');
  try {
    const cfg = await fetchConfig();
    fillForm(cfg);
  } catch (e) {
    status('Failed to load configuration', false);
  }
  form.addEventListener('submit', async (ev) => {
    ev.preventDefault();
    // simple client-side validation
    const hotkey = document.getElementById('hotkey').value.trim();
    if (!hotkey) {
      status('Hotkey cannot be empty', false);
      return;
    }
    form.setAttribute('aria-busy', 'true');
    status('Saving...');
    if (saveBtn) saveBtn.disabled = true;
    try {
      const result = await postConfig(readForm());
      if (result && result.ok) {
        status('Saved!');
      } else {
        status(result && result.error ? result.error : 'Save failed', false);
      }
    } catch (e) {
      status('Save failed', false);
    } finally {
      form.setAttribute('aria-busy', 'false');
      if (saveBtn) saveBtn.disabled = false;
    }
  });
  if (testBtn) testBtn.addEventListener('click', startHotkeyTest);
  if (stopBtn) stopBtn.addEventListener('click', stopHotkeyTest);
  if (beepBtn) beepBtn.addEventListener('click', beepPreview);
  if (hotkeyInput) hotkeyInput.addEventListener('input', (e) => {
    const val = e.target.value.trim();
    if (_hkTimer) window.clearTimeout(_hkTimer);
    _hkTimer = window.setTimeout(() => validateHotkeyLive(val), 150);
  });
  resetBtn.addEventListener('click', async () => {
    try {
      const cfg = await fetchConfig();
      fillForm(cfg);
      status('Reset to current values');
      // clear any previous error displays
      validateHotkeyLive(document.getElementById('hotkey').value.trim());
    } catch (e) {
      status('Failed to reload configuration', false);
    }
  });
});
