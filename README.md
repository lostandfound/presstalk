# PressTalk CLI

Local push‑to‑talk (PTT) with offline ASR. macOS-oriented, works entirely locally (no server required).

- Design: docs/design.md
- Usage: docs/usage.md

## Install

Recommended with uv (or pip):

```bash
# Inside this repo (editable dev install)
uv pip install -e presstalk[all]

# Or, when published to PyPI (example)
# uv pip install presstalk[all]
```

Extras:
- `[engine]` faster-whisper + numpy
- `[capture]` sounddevice
- `[hotkey]` pynput
- `[all]` everything above

## Run (examples)

```bash
uv run presstalk simulate --chunks hello world --delay-ms 40

uv run presstalk run \
  --mode hold --global-hotkey --hotkey ctrl \
  --language ja --model small --prebuffer-ms 200 --min-capture-ms 1800
```

See docs/usage.md for full instructions and permissions.
