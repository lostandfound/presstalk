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

Clone first:
```bash
git clone https://github.com/lostandfound/presstalk.git
cd presstalk
```

Option A — No-CD (recommended, 1-step setup):
```bash
make bootstrap
# then from anywhere
presstalk
```

Option B — Project-local venv:
```bash
uv venv && source .venv/bin/activate
uv pip install -e .
uv run presstalk
```
Tips:
- On first run, macOS prompts for Microphone and Accessibility permissions.
- Hold the chosen key (default `ctrl`) to record. When you release it, PressTalk transcribes locally and pastes the text at your current cursor position in the active app.
- Paste guard is enabled by default: paste is skipped when Terminal/iTerm is frontmost (configurable).
  - Tip: `presstalk` with no args equals `presstalk run`.

## What It Does
- Voice input for any text field: record while holding a key, paste on release.
- Global hotkey by default (`ctrl`), configurable via YAML or CLI.
- Offline ASR with faster‑whisper; audio never leaves your device.
- Paste guard avoids Terminal/iTerm by default; customize via YAML.

## Makefile Shortcuts
- `make venv && source .venv/bin/activate && make install`
- `make run` / `make console`
- `make simulate CHUNKS="hello world" DELAY=40`
- `make test` / `make test-file FILE=tests/test_controller.py`
- `make lint` / `make format` / `make typecheck`

## No-CD Setup (Run from anywhere)
- One-shot setup (auto-detects uv/pipx/venv):
  - `make bootstrap`
  - Then run globally: `presstalk run` (or `pt` if alias was added)
- Quick global install (uv):
  - `make install-global` and ensure `~/.local/bin` is in PATH (`make path-zsh` or `make path-bash`)
- Run now without install (from repo):
  - `make run-anywhere`

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

- Python 3.9+ on macOS 13+, Windows 10/11, or Linux.
- Build tools (macOS): `xcode-select --install`.
- Audio backend (macOS, if `sounddevice` build fails): `brew install portaudio`.
- Permissions: macOS requires Microphone + Accessibility; Windows requires a focused text input to paste.

Note: Docker is not supported for runtime use (microphone, global hotkeys, and paste require host permissions).

## Run (examples)

```bash
uv run presstalk simulate --chunks hello world --delay-ms 40

uv run presstalk run \
  --mode hold \
  --language ja --model small --prebuffer-ms 200 --min-capture-ms 1800
```

See docs/usage.md for full instructions (including Windows/Linux notes) and permissions.
