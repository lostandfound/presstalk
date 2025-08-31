# PressTalk CLI

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

Language: [English](README.md) | [日本語](README-ja.md)

Local voice input tool using push‑to‑talk (PTT). Hold a control key to record; release to insert transcribed text at the cursor in the frontmost app. Runs entirely on your machine (no server). macOS, Windows, and Linux are supported.

- Architecture: docs/architecture.md
- Roadmap: docs/ROADMAP.md
- Usage: docs/usage.md
- 日本語: docs/usage-ja.md
- 日本語 README: README-ja.md
- Commands: docs/commands.md

## Quick Start

Option A — One-shot (global, recommended)
```bash
uv run python task.py bootstrap
# then from anywhere
presstalk
```

Option B — Local dev (project venv)
```bash
uv venv && source .venv/bin/activate
uv pip install -e .
# Run locally (global hotkey) or console mode
uv run presstalk
uv run presstalk --console
```
Notes:
- macOS prompts for Microphone + Accessibility on first run.
- Hold the key (default `ctrl`) to record; release to paste.

## What It Does
- Voice input for any text field: record while holding a key, paste on release.
- Global hotkey by default (`ctrl`), configurable via YAML or CLI.
- Offline ASR with faster‑whisper; audio never leaves your device.
- Paste guard avoids Terminal/iTerm by default; customize via YAML.

## Tasks (Cross-Platform)
Use the task runner for common workflows:
- Install: `uv run python task.py install`
- Test: `uv run python task.py test`
- Simulate: `uv run python task.py simulate --chunks hello world --delay-ms 40`
- Run: `uv run python task.py run` (or `--console`)

For Unix users, a Makefile wrapper exists but is optional. See docs.

## Configuration (YAML)
- Auto-discovery: `presstalk.yaml` in the repository root (editable installs).
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
paste_guard: true
paste_blocklist:
  - Terminal
  - iTerm2
  - com.apple.Terminal
  - com.googlecode.iterm2
```

### Console Input mode (optional)

```bash
uv run presstalk run --console
```
- Type `p` then `r` to record/release, `q` to quit (no global hotkey).

## Docs
- Usage: docs/usage.md (Windows/macOS/Linux notes, YAML config, Makefile wrapper)
- 日本語: docs/usage-ja.md
- Commands: docs/commands.md

## Dependencies

- Python 3.9+ on macOS 13+, Windows 10/11, or Linux.
- Build tools (macOS): `xcode-select --install`.
- Audio backend (macOS, if `sounddevice` build fails): `brew install portaudio`.
- Permissions: macOS requires Microphone + Accessibility; Windows requires a focused text input to paste.

Note: Docker is not supported for runtime use (microphone, global hotkeys, and paste require host permissions).

For advanced setup (global install, run-anywhere), see docs.
