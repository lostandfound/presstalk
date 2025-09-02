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
  - Model options: `tiny`/`base`/`small`/`medium`/`large`/`large-v3` (speed vs accuracy tradeoff)
  - Language support: 99 languages including Japanese (`ja`) and English (`en`)
  - Lazy loading: Models downloaded on first use, cached locally
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

### Model Selection Guidelines
| Model | Speed | Accuracy | Memory* | Use Case |
|-------|-------|----------|---------|----------|
| `tiny` | Fastest | Lowest | ~40MB | Quick testing, resource-constrained |
| `base` | Fast | Good | ~75MB | Development, fast feedback |
| `small` | Balanced | Very Good | ~245MB | **Recommended default** |
| `medium` | Slower | Excellent | ~770MB | High accuracy needs |
| `large-v3` | Slowest | Best | ~1.5GB | Production, maximum precision |

*Memory usage shown is for CPU execution with faster-whisper optimization. GPU usage would be higher.

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

## See Also

- [Release Process](dev/RELEASE.md) - Version numbering, release planning, and comprehensive release workflow
- [GitHub Workflow](dev/GITHUB.md) - Issue management and PR guidelines
- [Usage Guide](usage.md) - User installation and configuration
- [Commands Reference](commands.md) - CLI options and usage examples
