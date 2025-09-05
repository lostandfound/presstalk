# Migration Guide: v0.x → v1.0.0

This guide helps existing users upgrade smoothly to v1.0.0. The primary breaking change is the default global hotkey. New audio feedback and configuration interfaces are also introduced.

## TL;DR Quick Start

```bash
# Update your hotkey configuration interactively
presstalk config

# Or edit presstalk.yaml directly
hotkey: ctrl+space
```

## What Changed (Breaking)

- Default hotkey: `ctrl` → `ctrl+space`
  - Reason: avoid screen reader conflicts (e.g., NVDA/JAWS speech interruption), align with two-key ergonomics, and improve overall accessibility.
  - Decision record: see docs/adr/ADR-001-default-hotkey-change.md

## Why the Change?

- Screen reader conflicts: Single-key modifiers like `ctrl` are commonly used to pause/resume speech or navigate. Using `ctrl` alone can interrupt assistive technologies.
- Two-key ergonomics: `ctrl+space` reduces accidental activation and matches common PTT ergonomics.
- Accessibility: Minimizes interference with assistive tech usage and supports responsible defaults. Related guidance: WCAG 2.1 (Keyboard and Avoid Keyboard Trap).

## Configuration Options

- Keep the old behavior (not recommended):
  - Run `presstalk config` and set Hotkey to `ctrl`.
  - Or in YAML: `hotkey: ctrl`.
- Choose a different combo:
  - Examples: `ctrl+shift+x`, `cmd+space`, `alt+space` (platform policy permitting).
  - Combinations are normalized and validated; see docs/adr/ADR-001-default-hotkey-change.md for details.
- Audio feedback settings:
  - `audio_feedback: true|false` in YAML.
  - CLI/Web config also expose a toggle and a “Beep” preview.

## New Features in v1.0.0

- Interactive configuration (CLI): `presstalk config`
- Web-based configuration (local only): `presstalk config --web` → http://127.0.0.1:8765
- System beep feedback for recording state (start/stop cues)

## Before / After Examples

YAML prior to v1.0.0 (common setup):
```yaml
hotkey: ctrl
```

YAML after migrating to v1.0.0 (recommended):
```yaml
hotkey: ctrl+space
audio_feedback: true
```

## Troubleshooting

- Hotkey does not trigger:
  - macOS: Ensure Accessibility permission is granted to your terminal/app. Check for conflicts with input source switching (System Settings → Keyboard → Shortcuts → Input Sources; `Ctrl+Space` may be assigned by default on some locales; change or disable it).
  - Windows: Ensure a text field is focused for paste. Some accessibility tools may bind `Ctrl`/`Ctrl+Space`—reassign in those tools if needed.
  - Linux/Wayland: Some compositors restrict global hotkeys and keystroke injection. Use `--console` mode or adjust compositor shortcuts. Install `wl-clipboard` as needed.
- Paste does not occur:
  - Verify “paste guard” is not blocking your current app; customize `paste_blocklist` if required.
  - Confirm clipboard access and permissions on your platform.
- Unintended activation or conflicts:
  - Pick a different two-key combo, e.g., `ctrl+shift+space` or `alt+space`.

## References

- Decision: docs/adr/ADR-001-default-hotkey-change.md
- Hotkey research: docs/knowledge/report-hotkey.md
- WCAG 2.1 (Keyboard, Keyboard Trap): https://www.w3.org/TR/WCAG21/

