# PressTalk Usage (macOS/Windows/Linux, Local-Only)

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

## 7) Cross-Platform Tasks (no Make)
- Prefer these commands on Windows/macOS/Linux to avoid shell differences:
```bash
uv run python task.py install
uv run python task.py test
uv run python task.py simulate --chunks hello world --delay-ms 40
uv run python task.py run          # global hotkey
uv run python task.py run --console
uv run python task.py clean
```

## 8) Recommended Settings
- Language: `--language ja`
- Model: `--model small`
- Prebuffer: `--prebuffer-ms 0..300`
- Minimum capture: `--min-capture-ms 1800`

## 9) Troubleshooting
- `sounddevice` errors: `brew install portaudio` then reinstall
- First run is slow: model download/cache; subsequent runs are faster
- No paste: check Accessibility permission and text focus in the frontmost app
- Too short utterances: raise `min_capture_ms` or use small prebuffer

## 10) Linux Notes
- Recommended packages (Debian/Ubuntu):
```bash
sudo apt-get update && sudo apt-get install -y \
  portaudio19-dev libasound2-dev xclip xdotool
```
- Wayland: install `wl-clipboard` for clipboard support; keystroke injection may be restricted by the compositor. Prefer `--console` mode if global key events are blocked.
```bash
sudo apt-get install -y wl-clipboard
```
- Setup is otherwise the same: create venv, `uv pip install -e .`, then `simulate`/`run --console`.
- Paste guard defaults include common Linux terminals; override with YAML `paste_blocklist:` or `PT_PASTE_BLOCKLIST`.

## 11) Windows Notes
- Use Windows Terminal for proper ANSI color rendering.
- Ensure audio devices are working; `sounddevice` uses PortAudio on Windows.
- Clipboard and paste guard require a focused text input in the foreground app.

## 12) Environment Variables (optional)
- `PT_LANGUAGE`, `PT_SAMPLE_RATE`, `PT_CHANNELS`, `PT_PREBUFFER_MS`, `PT_MIN_CAPTURE_MS`, `PT_MODEL`
- `PT_PASTE_GUARD`, `PT_PASTE_BLOCKLIST`

### Paste Guard defaults
- macOS default blocklist: `Terminal,iTerm2,com.apple.Terminal,com.googlecode.iterm2`
- Windows default blocklist: `cmd.exe,powershell.exe,pwsh.exe,WindowsTerminal.exe,wt.exe,conhost.exe`
You can override with YAML `paste_blocklist:` or `PT_PASTE_BLOCKLIST`.

Note: Docker is not supported for runtime (device/GUI constraints).
