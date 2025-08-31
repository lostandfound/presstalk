import os
from dataclasses import dataclass
from typing import Optional, Any, Dict

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
    # Paste
    paste_guard: Optional[bool] = None
    paste_blocklist: Optional[Any] = None
    # UI misc
    show_logo: Optional[bool] = None
    # Source
    config_path: Optional[str] = None

    def __post_init__(self):
        data = self._load_yaml(self.config_path)
        # base defaults
        lang = "ja"
        sr = 16000
        ch = 1
        pre = 1000
        mincap = 1800
        mdl = "small"
        mde = "hold"
        hk = "ctrl"
        pguard = True
        pblock = "Terminal,iTerm2,com.apple.Terminal,com.googlecode.iterm2"
        slog = True
        # overlay YAML
        if data:
            lang = data.get("language", lang)
            sr = int(data.get("sample_rate", sr))
            ch = int(data.get("channels", ch))
            pre = int(data.get("prebuffer_ms", pre))
            mincap = int(data.get("min_capture_ms", mincap))
            mdl = data.get("model", mdl)
            mde = data.get("mode", mde)
            hk = data.get("hotkey", hk)
            if "paste_guard" in data:
                try:
                    pguard = bool(data.get("paste_guard"))
                except Exception:
                    pass
            if "paste_blocklist" in data:
                pblock = data.get("paste_blocklist", pblock)
            if "show_logo" in data:
                try:
                    slog = bool(data.get("show_logo"))
                except Exception:
                    pass
        # overlay ENV
        lang = os.getenv("PT_LANGUAGE", lang)
        sr = int(os.getenv("PT_SAMPLE_RATE", str(sr)))
        ch = int(os.getenv("PT_CHANNELS", str(ch)))
        pre = int(os.getenv("PT_PREBUFFER_MS", str(pre)))
        mincap = int(os.getenv("PT_MIN_CAPTURE_MS", str(mincap)))
        mdl = os.getenv("PT_MODEL", mdl)
        # paste guard envs
        env_guard = os.getenv("PT_PASTE_GUARD")
        if env_guard is not None:
            pguard = env_guard not in ("0", "false", "False")
        pblock = os.getenv("PT_PASTE_BLOCKLIST", pblock)
        env_logo = os.getenv("PT_NO_LOGO")
        if env_logo is not None:
            # PT_NO_LOGO=1 disables logo
            slog = False if env_logo not in ("0", "false", "False") else slog
        # assign with explicit overrides last
        self.language = self.language or lang
        self.sample_rate = int(self.sample_rate or sr)
        self.channels = int(self.channels or ch)
        self.prebuffer_ms = int(self.prebuffer_ms or pre)
        self.min_capture_ms = int(self.min_capture_ms or mincap)
        self.model = self.model or mdl
        # ui (no env vars defined; YAML or explicit only)
        self.mode = self.mode or mde
        self.hotkey = self.hotkey or hk
        # paste
        if self.paste_guard is None:
            self.paste_guard = pguard
        if self.paste_blocklist is None:
            self.paste_blocklist = pblock
        if self.show_logo is None:
            self.show_logo = slog

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
                if '#' in line:
                    line = line.split('#', 1)[0].rstrip()
                if not line or line.startswith('#'):
                    continue
                if in_list and line.startswith('-'):
                    item = line[1:].strip()
                    # best-effort typing
                    if item.lower() in ('true', 'false'):
                        val: Any = item.lower() == 'true'
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
                if ':' in line:
                    k, v = line.split(':', 1)
                    k = k.strip()
                    v = v.strip()
                    if v == '':
                        # beginning of list section
                        key = k
                        in_list = True
                        cur_list = []
                        continue
                    # bracket list: [a, b, c]
                    if v.startswith('[') and v.endswith(']'):
                        items = [s.strip() for s in v[1:-1].split(',') if s.strip()]
                        coerced = []
                        for item in items:
                            if item.lower() in ('true', 'false'):
                                coerced.append(item.lower() == 'true')
                            else:
                                try:
                                    coerced.append(int(item))
                                except Exception:
                                    coerced.append(item)
                        data[k] = coerced
                        continue
                    # best-effort typing
                    if v.lower() in ('true', 'false'):
                        val = v.lower() == 'true'
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
