# PressTalk Usage (macOS, Local-Only)

## Prerequisites
- macOS 13+ (Apple Silicon or Intel)
- Python 3.9+
- Command Line Tools: `xcode-select --install`
- uv installed: https://docs.astral.sh/uv/

## 1) Environment
```bash
uv venv
source .venv/bin/activate
```

## 2) Install
```bash
uv pip install -e .
```
If `sounddevice` fails to build/install:
```bash
brew install portaudio
```
Then rerun the install command.

## 3) Permissions (macOS)
- Microphone: allow on first capture.
- Accessibility: enable your terminal app for global hotkeys and paste.

## 4) Configuration (YAML)
- Auto-discovery: `presstalk.yaml` in the repository root (editable installs).
- Override path: `uv run presstalk run --config path/to/config.yaml`
- Example
```yaml
language: ja
model: small
sample_rate: 16000
channels: 1
prebuffer_ms: 200
min_capture_ms: 1800
mode: hold       # hold or toggle
hotkey: ctrl     # ctrl/cmd/alt/space or key
paste_guard: true
paste_blocklist:
  - Terminal
  - iTerm2
  - com.apple.Terminal
  - com.googlecode.iterm2
show_logo: true
```

## 5) Quick Check (Simulated)
```bash
uv run presstalk simulate --chunks hello world --delay-ms 40
```
Expect: a final line like `FINAL: bytes=...`.

## 6) Run (Local PTT)
- Global hotkey (default):
```bash
uv run presstalk run
```
Press the hotkey (default `ctrl`) to record; release to finalize and paste.

- Console mode (alternative):
```bash
uv run presstalk run --console
```
Type `p` + Enter to press, `r` + Enter to release, `q` to quit.

## 7) Recommended Settings
- Language: `--language ja`
- Model: `--model small`
- Prebuffer: `--prebuffer-ms 0..300`
- Minimum capture: `--min-capture-ms 1800`

## 8) Troubleshooting
- `sounddevice` errors: `brew install portaudio` then reinstall
- First run is slow: model download/cache; subsequent runs are faster
- No paste: check Accessibility permission and text focus in the frontmost app
- Too short utterances: raise `min_capture_ms` or use small prebuffer

## 9) Environment Variables (optional)
- `PT_LANGUAGE`, `PT_SAMPLE_RATE`, `PT_CHANNELS`, `PT_PREBUFFER_MS`, `PT_MIN_CAPTURE_MS`, `PT_MODEL`
- `PT_PASTE_GUARD`, `PT_PASTE_BLOCKLIST`

Note: Docker is not supported for runtime (device/GUI constraints).
