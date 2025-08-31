# Architecture Overview

## High-Level Flow
- Global hotkey (default) or console input triggers press/release.
- Capture (sounddevice) writes PCM to `RingBuffer` continuously.
- On press, `Controller` pushes prebuffer tail; while holding, live PCM is streamed to the `AsrEngine`.
- On release, `Controller` finalizes the engine session and `Orchestrator` pastes the text (guarded) to the frontmost app.

## Components
- CLI (`src/presstalk/cli.py`): Parses args, loads YAML config, wires the system, and selects hotkey vs console mode.
- Config (`src/presstalk/config.py`): Merges YAML → ENV → CLI with defaults. YAML auto-discovery and `--config` path supported.
- Capture (`src/presstalk/capture.py`, `capture_sd.py`): Pull-based PCM source (CoreAudio via `sounddevice`).
- Engine (`src/presstalk/engine/*`): `FasterWhisperBackend` + `FasterWhisperEngine` implement `AsrEngine` protocol.
- Controller (`src/presstalk/controller.py`): Press/Release state machine, prebuffer push, live push, and finalize.
- Orchestrator (`src/presstalk/orchestrator.py`): Coordinates capture lifecycle and pasting.
- Paste (`src/presstalk/paste.py`): platform-dispatching `insert_text`.
  - macOS: `paste_macos.py` (pbcopy + osascript Cmd+V)
  - Windows: `paste_windows.py` (clip.exe + pynput Ctrl+V)
  - Linux: `paste_linux.py` (wl-copy/xclip/xsel + pynput or xdotool)

## Key Interfaces
```python
class AsrEngine:
    def start_session(self, language: str = 'ja') -> str: ...
    def push_audio(self, session_id: str, pcm_bytes: bytes) -> None: ...
    def finalize(self, session_id: str, timeout_s: float = 10.0) -> str: ...
    def close_session(self, session_id: str) -> None: ...

class RingBuffer:
    def write(self, pcm_bytes: bytes) -> None: ...
    def snapshot_tail(self, n_bytes: int) -> bytes: ...
```

## Configuration & Defaults
- YAML keys: `language`, `model`, `sample_rate`, `channels`, `prebuffer_ms`, `min_capture_ms`, `mode`, `hotkey`, `paste_guard`, `paste_blocklist`.
- Precedence: CLI > Env (`PT_*`) > YAML > built-ins.
- Local `presstalk.yaml` is auto-used if present; otherwise XDG/Home is probed.

## Logging & UX
- `_StatusOrch` provides minimal status logs: Recording / Finalizing / Stats / Engine time.
- `presstalk.logger` offers `QUIET|INFO|DEBUG`.

## Platform Considerations
- macOS: requires Microphone + Accessibility permissions.
- Docker: not supported for runtime (device/GUI constraints).

## Directory Layout
```
docs/
  architecture.md
  usage.md
  commands.md
src/presstalk/
  cli.py config.py controller.py capture.py capture_sd.py paste_macos.py
  engine/
    fwhisper_backend.py fwhisper_engine.py
tests/
  test_*.py
```

