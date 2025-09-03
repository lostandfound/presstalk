from typing import Optional, Set, List, Dict

try:
    from pynput import keyboard
except Exception:  # pragma: no cover - optional dep
    keyboard = None  # type: ignore

from .hotkey import HotkeyHandler


# ---- Hotkey parsing and validation ----

_MOD_ALIASES: Dict[str, str] = {
    "control": "ctrl",
    "ctl": "ctrl",
    "ctrl": "ctrl",
    "command": "cmd",
    "cmd": "cmd",
    "win": "cmd",
    "meta": "cmd",
    "option": "alt",
    "alt": "alt",
    "shift": "shift",
}

_KNOWN_NONMOD_ALIASES: Dict[str, str] = {
    "spacebar": "space",
    " ": "space",
}

_MOD_ORDER = ["cmd", "ctrl", "alt", "shift"]


def normalize_hotkey(spec: str) -> str:
    """Normalize a hotkey spec to canonical lowercase form.

    Examples:
    - "Control+Shift+X" -> "ctrl+shift+x"
    - "Cmd+Option+V" -> "cmd+alt+v"
    - "SHIFT+SPACE" -> "shift+space"
    """
    if not spec:
        return ""
    parts = [p.strip() for p in str(spec).split("+") if p.strip()]
    mods: Set[str] = set()
    primary: Optional[str] = None
    for p in parts:
        low = p.lower()
        if low in _MOD_ALIASES:
            mods.add(_MOD_ALIASES[low])
            continue
        if low in _KNOWN_NONMOD_ALIASES:
            low = _KNOWN_NONMOD_ALIASES[low]
        # single character key is fine
        primary = low
    # order modifiers canonically
    ordered = [m for m in _MOD_ORDER if m in mods]
    if primary:
        ordered.append(primary.lower())
    return "+".join(ordered)


def validate_hotkey(spec: str) -> bool:
    """Validate a hotkey combination string.

    Rules:
    - Allow one non-modifier key optionally combined with modifiers.
    - Allow legacy single-modifier hotkeys (e.g., "ctrl").
    - Disallow multiple modifiers with no primary (e.g., "ctrl+alt").
    - Disallow empty specs.
    """
    norm = normalize_hotkey(spec)
    if not norm:
        return False
    parts = norm.split("+")
    mods = [p for p in parts if p in _MOD_ORDER]
    nonmods = [p for p in parts if p not in _MOD_ORDER]
    if len(nonmods) > 1:
        return False
    if len(nonmods) == 1:
        # If we can introspect pynput, ensure multi-char token exists in keyboard.Key
        primary = nonmods[0]
        if len(primary) > 1 and keyboard is not None:
            try:
                if not hasattr(keyboard.Key, primary):
                    return False
            except Exception:
                pass
        return True
    # no primary: legacy single-modifier like "ctrl" ok; multiple modifiers invalid
    return len(mods) == 1


class GlobalHotkeyRunner:
    """Global hotkey listener using pynput, delegating to HotkeyHandler.

    Requires Accessibility permission on macOS.
    """

    def __init__(
        self, orchestrator, *, mode: str = "hold", key_name: str = "ctrl+shift+space"
    ) -> None:
        if keyboard is None:
            raise RuntimeError("pynput is not installed")
        self._handler = HotkeyHandler(orchestrator, mode=mode)
        self._key_spec = normalize_hotkey(key_name or "ctrl+shift+space")
        if not validate_hotkey(self._key_spec):
            raise ValueError(f"Invalid hotkey: {key_name}")
        self._listener: Optional[keyboard.Listener] = None
        # State for combo matching
        self._pressed: Set = set()
        self._required_groups: List[Set] = []
        self._combo_active = False
        self._build_required_groups()

    def _build_required_groups(self) -> None:
        parts = self._key_spec.split("+") if self._key_spec else []
        mods = [p for p in parts if p in _MOD_ORDER]
        nonmods = [p for p in parts if p not in _MOD_ORDER]
        # For each modifier, accept either side variants
        for m in mods:
            variants: Set = set()
            base = m
            keyobj = getattr(keyboard.Key, base, None)
            if keyobj is not None:
                variants.add(keyobj)
            for suffix in ("_l", "_r"):
                keyobj = getattr(keyboard.Key, base + suffix, None)
                if keyobj is not None:
                    variants.add(keyobj)
            # fallback to string token if unknown
            if not variants:
                variants.add(m)
            self._required_groups.append(variants)
        # Primary key group
        if nonmods:
            k = nonmods[0]
            if hasattr(keyboard.Key, k):
                self._required_groups.append({getattr(keyboard.Key, k)})
            else:
                # treat as character key
                self._required_groups.append({k})

    def _on_press(self, key):
        token = getattr(key, "char", None)
        if token is not None:
            token = str(token).lower()
            if token == " ":
                token = "space"
            self._pressed.add(token)
        else:
            self._pressed.add(key)
        self._update_combo_state()

    def _on_release(self, key):
        token = getattr(key, "char", None)
        if token is not None:
            token = str(token).lower()
            if token == " ":
                token = "space"
            self._pressed.discard(token)
        else:
            self._pressed.discard(key)
        self._update_combo_state()

    def _is_combo_active(self) -> bool:
        if not self._required_groups:
            return False
        # Legacy single-modifier hotkey: treat as active if that modifier is pressed
        for group in self._required_groups:
            # each group must have at least one member present
            if not any(tok in self._pressed for tok in group):
                return False
        return True

    def _update_combo_state(self) -> None:
        active = self._is_combo_active()
        if active and not self._combo_active:
            self._combo_active = True
            self._handler.handle_key_down()
        elif not active and self._combo_active:
            self._combo_active = False
            self._handler.handle_key_up()

    def start(self) -> None:
        self._listener = keyboard.Listener(
            on_press=self._on_press, on_release=self._on_release
        )
        self._listener.start()

    def stop(self) -> None:
        if self._listener:
            self._listener.stop()
            self._listener.join(timeout=1.0)
            self._listener = None
