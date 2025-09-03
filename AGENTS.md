# Repository Guidelines

## Project Structure & Module Organization
- Source: `src/presstalk/` (CLI in `cli.py`, runtime config in `config.py`, audio in `capture*.py`, hotkeys in `hotkey*.py`, engine backends under `engine/`).
- Hotkey combos: parsing/validation via `normalize_hotkey`/`validate_hotkey` in `hotkey_pynput.py`.
- Tests: `tests/` (`test_*.py`, uses `unittest`).
- Docs: `docs/` (`usage.md`, `design.md`).
- Packaging: `pyproject.toml` (entrypoint `presstalk = presstalk.cli:main`).

## Build, Test, and Development Commands
- Create venv: `uv venv && source .venv/bin/activate`
- Install (editable): `uv pip install -e .`
- Run CLI (simulated): `uv run presstalk simulate --chunks hello world --delay-ms 40`
- Run CLI (local): `uv run presstalk run` (global hotkey by default)
- Default hotkey: `shift+space` (combos allowed; e.g., `--hotkey ctrl+shift+x`).
- Use YAML config: `uv run presstalk run --config ./presstalk.yaml`
- Tests: `uv run python -m unittest -v` (discovers `tests/test_*.py`).

## Coding Style & Naming Conventions
- Python 3.9+; follow PEP 8 with 4‑space indentation and type hints where practical.
- Modules and files: `snake_case.py`; classes: `CamelCase`; functions/vars: `snake_case`.
- Keep functions small, side‑effect free, and log via `presstalk.logger` (use `get_logger()`; levels `QUIET|INFO|DEBUG`).
- Public API surfaces (e.g., controller/engine interfaces) should remain stable; prefer protocol-like patterns used in `controller.py`.

## Testing Guidelines
- Framework: standard library `unittest`.
- Naming: place tests in `tests/` as `test_<module>.py`, classes `Test<Thing>`.
- Coverage: prioritize core modules (`controller`, `orchestrator`, `capture`, `engine/*`). Add fast, deterministic tests; avoid device/network in unit tests.
- Hotkey combos covered in `tests/test_hotkey_combo.py`; unit tests avoid device hooks/pynput OS-level listeners.
- Run a focused file: `uv run python -m unittest tests/test_controller.py -v`.

## Commit & Pull Request Guidelines
- Commits: imperative present (“Add ring buffer snapshot”), small and scoped. Reference issues in body when relevant.
- Branches: short, descriptive (e.g., `feat/global-hotkey`, `fix/capture-timeout`).
- PRs: include purpose, summary of changes, testing notes, and screenshots/log snippets when UX/logging changes. Link related issues.
- CI not configured; run unit tests locally and verify `uv run presstalk simulate` works before requesting review.

## Security & Configuration Tips
- macOS permissions required: Microphone and Accessibility (for paste/hotkey). See `docs/usage.md`.
- Configuration: YAML at repository root (`presstalk.yaml`) is auto-used for editable installs; CLI `--config` overrides; env vars still supported (`PT_LANGUAGE`, etc.).
- Linux/Wayland may restrict global hotkeys; see limitations and guidance in `docs/knowledge/report-hotkey.md`.

## References
- ADR: `docs/adr/ADR-001-default-hotkey-change.md` (default hotkey changed to `shift+space`).
