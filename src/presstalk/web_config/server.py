from __future__ import annotations

import json
import webbrowser
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from typing import Optional, Tuple

from ..config import Config
from ..constants import MODEL_CHOICES


def _repo_root() -> Path:
    # src/presstalk -> repo root
    return Path(__file__).resolve().parents[2]


def _discover_config_path(explicit: Optional[str]) -> Optional[str]:
    if explicit:
        return explicit
    # mirror CLI behavior: prefer repo-root presstalk.yaml when running from repo
    repo_root = _repo_root()
    candidate = repo_root / "presstalk.yaml"
    return str(candidate) if candidate.is_file() else None


class _Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, static_dir: Path, cfg_path: Optional[str], **kwargs):
        self._static_dir = static_dir
        self._cfg_path = cfg_path
        super().__init__(*args, directory=str(static_dir), **kwargs)

    def _send_json(self, obj, status: int = 200) -> None:
        data = json.dumps(obj).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _read_json(self) -> Tuple[dict, Optional[str]]:
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except Exception:
            length = 0
        # Enforce a small request size limit (8 KiB)
        max_len = 8192
        if length > max_len:
            return {}, "request too large"
        raw = self.rfile.read(length) if length > 0 else b""
        try:
            obj = json.loads(raw.decode("utf-8") or "{}")
            return obj, None
        except Exception as e:
            return {}, f"invalid json: {e}"

    def do_GET(self):  # noqa: N802 - stdlib signature
        if self.path.startswith("/api/config"):
            cfg = Config(config_path=self._cfg_path)
            self._send_json(
                {
                    "language": cfg.language,
                    "model": cfg.model,
                    "hotkey": cfg.hotkey,
                    "audio_feedback": bool(getattr(cfg, "audio_feedback", True)),
                }
            )
            return
        return super().do_GET()

    def do_POST(self):  # noqa: N802 - stdlib signature
        if self.path.startswith("/api/beep"):
            try:
                from ..beep import beep as system_beep
                system_beep()
            except Exception:
                pass
            self._send_json({"ok": True})
            return
        if self.path.startswith("/api/config"):
            payload, err = self._read_json()
            if err:
                self._send_json({"ok": False, "error": err}, status=400)
                return
            # Validate using existing helpers
            try:
                from ..hotkey_pynput import normalize_hotkey, validate_hotkey
            except Exception:
                def normalize_hotkey(x):  # type: ignore
                    return x

                def validate_hotkey(x):  # type: ignore
                    return bool(x)

            cfg = Config(config_path=self._cfg_path)
            # apply fields if present
            if "language" in payload and isinstance(payload["language"], str):
                cfg.language = payload["language"].strip() or cfg.language
            if "model" in payload and isinstance(payload["model"], str):
                m = payload["model"].strip().lower()
                if m in set(MODEL_CHOICES):
                    cfg.model = m
            if "hotkey" in payload and isinstance(payload["hotkey"], str):
                hk = normalize_hotkey(payload["hotkey"])  # type: ignore[arg-type]
                if validate_hotkey(hk):
                    cfg.hotkey = hk
            if "audio_feedback" in payload:
                cfg.audio_feedback = bool(payload["audio_feedback"])

            # write back to YAML (preserve comments if possible)
            try:
                from ..cli import _write_yaml_preserve_comments as writer
            except Exception:
                from ..cli import _write_yaml as writer  # fallback

            # Decide path: repo root or provided path or default repo path
            path = self._cfg_path or str((_repo_root() / "presstalk.yaml"))
            writer(
                path,
                {
                    "language": cfg.language,
                    "model": cfg.model,
                    "hotkey": cfg.hotkey,
                    "audio_feedback": bool(getattr(cfg, "audio_feedback", True)),
                },
            )
            self._send_json({"ok": True, "path": path})
            return
        return super().do_POST()


def serve_web_config(
    *, port: int = 8765, open_browser: bool = True, config_path: Optional[str] = None
) -> None:
    base = Path(__file__).resolve().parent
    static_dir = base / "static"
    cfg_path = _discover_config_path(config_path)

    def _handler(*args, **kwargs):  # type: ignore
        return _Handler(*args, static_dir=static_dir, cfg_path=cfg_path, **kwargs)

    httpd = HTTPServer(("127.0.0.1", port), _handler)

    url = f"http://127.0.0.1:{port}/"
    print(f"Web config running at {url}")
    if open_browser:
        try:
            webbrowser.open(url)
        except Exception:
            pass

    try:
        httpd.serve_forever()
    finally:
        try:
            httpd.server_close()
        except Exception:
            pass
