# PressTalk CLI

Local push‑to‑talk (PTT) with offline ASR. macOS-oriented, works entirely locally (no server required).

- Design: docs/design.md
- Usage: docs/usage.md

## Quick Start

```bash
uv venv && source .venv/bin/activate
uv pip install -e .

# Smoke test (no extra permissions needed)
uv run presstalk simulate

# Run (global hotkey is default)
uv run presstalk run
```
Tips:
- On first run, macOS prompts for Microphone and Accessibility permissions.
- Hold the chosen key (e.g., `ctrl`) to record; release to finalize and paste.

## Configuration (YAML)
- Auto-discovery: `./presstalk.yaml`, `$XDG_CONFIG_HOME/presstalk/config.yaml`, or `~/.presstalk.yaml`.
- Override path: `uv run presstalk run --config path/to/config.yaml`.
- Example:
```yaml
language: ja
model: small
sample_rate: 16000
channels: 1
prebuffer_ms: 200
min_capture_ms: 1800
mode: hold      # hold or toggle
hotkey: ctrl    # ctrl/cmd/alt/space or key
```

### Console Input mode (optional)

```bash
uv run presstalk run --console
```
- Type `p` then `r` to record/release, `q` to quit (no global hotkey).

## Install

Recommended with uv (or pip):

```bash
# Inside this repo (editable dev install)
uv pip install -e .

# Or, when published to PyPI (example)
# uv pip install presstalk
```

All runtime dependencies are included by default (pynput, faster-whisper, numpy, sounddevice).

## Dependencies

- Python 3.9+ on macOS 13+ recommended.
- Build tools: `xcode-select --install`.
- Audio backend (only if `sounddevice` build fails): `brew install portaudio`.
- Permissions: allow Microphone and Accessibility on first run.

## Run (examples)

```bash
uv run presstalk simulate --chunks hello world --delay-ms 40

uv run presstalk run \
  --mode hold \
  --language ja --model small --prebuffer-ms 200 --min-capture-ms 1800
```

See docs/usage.md for full instructions and permissions.
