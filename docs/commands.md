# Command Reference

## presstalk (CLI)
- Version: `presstalk --version`
- Subcommands: `run`, `simulate`

## run — Local PTT (default: global hotkey)
- `--config <path>`: YAML path. Auto: `./presstalk.yaml` if present.
- `--mode <hold|toggle>`: PTT mode. Defaults to YAML or `hold`.
- `--console`: Use console input instead of global hotkey.
- `--hotkey <key>`: Hotkey name (`ctrl|cmd|alt|space|a...`). Defaults to YAML or `ctrl`.
- `--log-level <QUIET|INFO|DEBUG>`: Logging level (default: `INFO`).
- `--language <code>`: Override language (e.g., `ja`).
- `--model <name>`: Override model (e.g., `small`).
- `--prebuffer-ms <int>`: Prebuffer ms (0..300 recommended).
- `--min-capture-ms <int>`: Minimum capture ms (e.g., 1800).

Examples
- `uv run presstalk run`
- `uv run presstalk run --mode toggle --hotkey cmd`
- `uv run presstalk run --config ./presstalk.yaml`

## simulate — Dummy source + engine (no devices)
- `--config <path>`: YAML path (affects audio params).
- `--chunks <list>`: ASCII chunk list (default: `aa bb cc`).
- `--delay-ms <int>`: Delay between chunks (default: `50`).

Examples
- `uv run presstalk simulate --chunks hello world --delay-ms 40`

## Configuration (YAML / Env)
- YAML auto-discovery: `./presstalk.yaml`, `$XDG_CONFIG_HOME/presstalk/config.yaml`, `~/.presstalk.yaml`.
- Keys: `language`, `model`, `sample_rate`, `channels`, `prebuffer_ms`, `min_capture_ms`, `mode`, `hotkey`, `paste_guard`, `paste_blocklist`.
- Env vars (optional): `PT_LANGUAGE`, `PT_SAMPLE_RATE`, `PT_CHANNELS`, `PT_PREBUFFER_MS`, `PT_MIN_CAPTURE_MS`, `PT_MODEL`, `PT_PASTE_GUARD`, `PT_PASTE_BLOCKLIST`.
- Precedence: CLI > Env > YAML > defaults.

Notes
- macOS permissions: Microphone + Accessibility required.
- Docker runtime is not supported (device/GUI constraints).
