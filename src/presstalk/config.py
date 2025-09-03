import os
from dataclasses import dataclass
import sys
from typing import Optional, Any, Dict
from .constants import is_env_enabled

try:
    import yaml  # type: ignore
except Exception:  # fallback if PyYAML missing
    yaml = None


@dataclass
class Config:
    # Core
    language: Optional[str] = None
    sample_rate: Optional[int] = None
    channels: Optional[int] = None
    prebuffer_ms: Optional[int] = None
    min_capture_ms: Optional[int] = None
    model: Optional[str] = None
    # UI
    mode: Optional[str] = None
    hotkey: Optional[str] = None
    audio_feedback: Optional[bool] = None
    # Paste
    paste_guard: Optional[bool] = None
    paste_blocklist: Optional[Any] = None
    # UI misc
    show_logo: Optional[bool] = None
    logo_style: Optional[str] = None  # 'simple' (default) or 'standard'
    # Source
    config_path: Optional[str] = None

    def __post_init__(self):
        data = self._load_yaml(self.config_path)
        defaults = self._get_defaults()
        envs = self._load_env()
        self._apply_overrides(defaults, data or {}, envs)

    def _get_defaults(self) -> Dict[str, Any]:
        lang = "ja"
        sr = 16000
        ch = 1
        pre = 1000
        mincap = 1800
        mdl = "small"
        mde = "hold"
        hk = "ctrl+space"
        pguard = True
        afeedback = True
        # OS-specific default paste guard blocklist
        if os.name == "nt" or sys.platform == "win32":  # type: ignore[name-defined]
            pblock = (
                "cmd.exe,powershell.exe,pwsh.exe,WindowsTerminal.exe,wt.exe,conhost.exe"
            )
        elif sys.platform.startswith("linux"):
            pblock = (
                "gnome-terminal,org.gnome.Terminal,konsole,xterm,alacritty,kitty,"
                "wezterm,terminator,tilix,xfce4-terminal,lxterminal,io.elementary.terminal"
            )
        else:
            pblock = "Terminal,iTerm2,com.apple.Terminal,com.googlecode.iterm2"
        slog = True
        lstyle = "standard"
        return {
            "language": lang,
            "sample_rate": sr,
            "channels": ch,
            "prebuffer_ms": pre,
            "min_capture_ms": mincap,
            "model": mdl,
            "mode": mde,
            "hotkey": hk,
            "audio_feedback": afeedback,
            "paste_guard": pguard,
            "paste_blocklist": pblock,
            "show_logo": slog,
            "logo_style": lstyle,
        }

    def _load_env(self) -> Dict[str, Any]:
        out: Dict[str, Any] = {}
        if (v := os.getenv("PT_LANGUAGE")) is not None:
            out["language"] = v
        if (v := os.getenv("PT_SAMPLE_RATE")) is not None:
            try:
                out["sample_rate"] = int(v)
            except Exception:
                pass
        if (v := os.getenv("PT_CHANNELS")) is not None:
            try:
                out["channels"] = int(v)
            except Exception:
                pass
        if (v := os.getenv("PT_PREBUFFER_MS")) is not None:
            try:
                out["prebuffer_ms"] = int(v)
            except Exception:
                pass
        if (v := os.getenv("PT_MIN_CAPTURE_MS")) is not None:
            try:
                out["min_capture_ms"] = int(v)
            except Exception:
                pass
        if (v := os.getenv("PT_MODEL")) is not None:
            out["model"] = v
        # paste guard envs
        if (v := os.getenv("PT_PASTE_GUARD")) is not None:
            out["paste_guard"] = is_env_enabled(v)
        if (v := os.getenv("PT_PASTE_BLOCKLIST")) is not None:
            out["paste_blocklist"] = v
        if (v := os.getenv("PT_NO_LOGO")) is not None:
            out["show_logo"] = not is_env_enabled(v)
        if (v := os.getenv("PT_LOGO_STYLE")) is not None:
            out["logo_style"] = v
        return out

    def _apply_overrides(
        self,
        defaults: Dict[str, Any],
        yaml_data: Dict[str, Any],
        env_data: Dict[str, Any],
    ) -> None:
        # Start from defaults
        vals: Dict[str, Any] = dict(defaults)
        # YAML overlay with basic typing coercion where used previously
        if yaml_data:

            def pick_int(name, cur):
                try:
                    return int(yaml_data.get(name, cur))
                except Exception:
                    return cur

            vals["language"] = yaml_data.get("language", vals["language"])
            vals["sample_rate"] = pick_int("sample_rate", vals["sample_rate"])
            vals["channels"] = pick_int("channels", vals["channels"])
            vals["prebuffer_ms"] = pick_int("prebuffer_ms", vals["prebuffer_ms"])
            vals["min_capture_ms"] = pick_int("min_capture_ms", vals["min_capture_ms"])
            vals["model"] = yaml_data.get("model", vals["model"])
            vals["mode"] = yaml_data.get("mode", vals["mode"])
            vals["hotkey"] = yaml_data.get("hotkey", vals["hotkey"])
            if "audio_feedback" in yaml_data:
                try:
                    vals["audio_feedback"] = bool(yaml_data.get("audio_feedback"))
                except Exception:
                    pass
            if "paste_guard" in yaml_data:
                try:
                    vals["paste_guard"] = bool(yaml_data.get("paste_guard"))
                except Exception:
                    pass
            if "paste_blocklist" in yaml_data:
                vals["paste_blocklist"] = yaml_data.get(
                    "paste_blocklist", vals["paste_blocklist"]
                )
            if "show_logo" in yaml_data:
                try:
                    vals["show_logo"] = bool(yaml_data.get("show_logo"))
                except Exception:
                    pass
            if "logo_style" in yaml_data:
                try:
                    ls = str(yaml_data.get("logo_style"))
                    vals["logo_style"] = ls or vals["logo_style"]
                except Exception:
                    pass
        # ENV overlay
        for k, v in env_data.items():
            vals[k] = v
        # Assign to self when not explicitly set
        self.language = self.language or vals["language"]
        self.sample_rate = int(self.sample_rate or vals["sample_rate"])
        self.channels = int(self.channels or vals["channels"])
        self.prebuffer_ms = int(self.prebuffer_ms or vals["prebuffer_ms"])
        self.min_capture_ms = int(self.min_capture_ms or vals["min_capture_ms"])
        self.model = self.model or vals["model"]
        self.mode = self.mode or vals["mode"]
        self.hotkey = self.hotkey or vals["hotkey"]
        if self.audio_feedback is None:
            self.audio_feedback = bool(vals.get("audio_feedback", True))
        # Normalize and validate hotkey specification
        try:
            from .hotkey_pynput import normalize_hotkey, validate_hotkey

            if self.hotkey:
                norm = normalize_hotkey(self.hotkey)
                if validate_hotkey(norm):
                    self.hotkey = norm
                else:
                    # fallback to safe default
                    self.hotkey = vals["hotkey"]
        except Exception:
            # best-effort: leave as-is if validation unavailable
            pass
        if self.paste_guard is None:
            self.paste_guard = vals["paste_guard"]
        if self.paste_blocklist is None:
            self.paste_blocklist = vals["paste_blocklist"]
        if self.show_logo is None:
            self.show_logo = vals["show_logo"]
        if self.logo_style is None:
            self.logo_style = vals["logo_style"]

    @property
    def bytes_per_second(self) -> int:
        return self.sample_rate * self.channels * 2

    @staticmethod
    def _load_yaml(path: Optional[str]) -> Dict[str, Any]:
        def _mini_yaml_parse(text: str) -> Dict[str, Any]:
            data: Dict[str, Any] = {}
            key = None
            in_list = False
            cur_list: list = []
            for raw in text.splitlines():
                line = raw.strip()
                if not line:
                    continue
                # strip inline comments (# ...)
                if "#" in line:
                    line = line.split("#", 1)[0].rstrip()
                if not line or line.startswith("#"):
                    continue
                if in_list and line.startswith("-"):
                    item = line[1:].strip()
                    # best-effort typing
                    if item.lower() in ("true", "false"):
                        val: Any = item.lower() == "true"
                    else:
                        try:
                            val = int(item)
                        except Exception:
                            val = item
                    cur_list.append(val)
                    continue
                # end current list if we see a new key
                if in_list:
                    data[key] = cur_list
                    in_list = False
                    cur_list = []
                    key = None
                if ":" in line:
                    k, v = line.split(":", 1)
                    k = k.strip()
                    v = v.strip()
                    if v == "":
                        # beginning of list section
                        key = k
                        in_list = True
                        cur_list = []
                        continue
                    # bracket list: [a, b, c]
                    if v.startswith("[") and v.endswith("]"):
                        items = [s.strip() for s in v[1:-1].split(",") if s.strip()]
                        coerced = []
                        for item in items:
                            if item.lower() in ("true", "false"):
                                coerced.append(item.lower() == "true")
                            else:
                                try:
                                    coerced.append(int(item))
                                except Exception:
                                    coerced.append(item)
                        data[k] = coerced
                        continue
                    # best-effort typing
                    if v.lower() in ("true", "false"):
                        val = v.lower() == "true"
                    else:
                        try:
                            val = int(v)
                        except Exception:
                            val = v
                    data[k] = val
            if in_list and key is not None:
                data[key] = cur_list
            return data

        def try_read(p: str) -> Optional[Dict[str, Any]]:
            try:
                if not os.path.isfile(p):
                    return None
                with open(p, "r", encoding="utf-8") as f:
                    text = f.read()
                if yaml is not None:
                    obj = yaml.safe_load(text) or {}
                    return obj if isinstance(obj, dict) else {}
                # fallback minimal parser (supports this project's keys)
                return _mini_yaml_parse(text)
            except Exception:
                return None

        # explicit path
        if path:
            found = try_read(path)
            return found or {}
        # search defaults (do not auto-read CWD here; CLI may pass it explicitly)
        candidates = []
        # XDG
        xdg = os.getenv("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))
        candidates.append(os.path.join(xdg, "presstalk", "config.yaml"))
        # legacy home
        candidates.append(os.path.expanduser("~/.presstalk.yaml"))
        for p in candidates:
            data = try_read(p)
            if data:
                return data
        return {}
