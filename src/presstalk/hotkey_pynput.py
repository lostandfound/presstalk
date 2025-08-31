from typing import Optional, Set

try:
    from pynput import keyboard
except Exception as e:  # pragma: no cover - optional dep
    keyboard = None  # type: ignore

from .hotkey import HotkeyHandler


class GlobalHotkeyRunner:
    """Global hotkey listener using pynput, delegating to HotkeyHandler.

    Requires Accessibility permission on macOS.
    """

    def __init__(self, orchestrator, *, mode: str = 'hold', key_name: str = 'ctrl') -> None:
        if keyboard is None:
            raise RuntimeError("pynput is not installed")
        self._handler = HotkeyHandler(orchestrator, mode=mode)
        self._key_name = (key_name or 'ctrl').lower()
        self._listener: Optional[keyboard.Listener] = None
        self._keys_to_watch: Set = set()
        self._build_keys()

    def _build_keys(self) -> None:
        # Map common modifier names; else treat as character key
        if self._key_name in ("ctrl", "control"):
            self._keys_to_watch.update({keyboard.Key.ctrl, getattr(keyboard.Key, "ctrl_l", keyboard.Key.ctrl)})
            if hasattr(keyboard.Key, "ctrl_r"):
                self._keys_to_watch.add(keyboard.Key.ctrl_r)
        elif self._key_name in ("cmd", "command"):
            self._keys_to_watch.update({keyboard.Key.cmd, getattr(keyboard.Key, "cmd_l", keyboard.Key.cmd)})
            if hasattr(keyboard.Key, "cmd_r"):
                self._keys_to_watch.add(keyboard.Key.cmd_r)
        elif self._key_name in ("alt", "option"):
            self._keys_to_watch.update({keyboard.Key.alt, getattr(keyboard.Key, "alt_l", keyboard.Key.alt)})
            if hasattr(keyboard.Key, "alt_r"):
                self._keys_to_watch.add(keyboard.Key.alt_r)
        else:
            # Use as character key, e.g., 'space' also mapped if name matches attribute
            if hasattr(keyboard.Key, self._key_name):
                self._keys_to_watch.add(getattr(keyboard.Key, self._key_name))
            else:
                self._keys_to_watch.add(self._key_name)

    def _on_press(self, key):
        if key in self._keys_to_watch or getattr(key, "char", None) in self._keys_to_watch:
            self._handler.handle_key_down()

    def _on_release(self, key):
        if key in self._keys_to_watch or getattr(key, "char", None) in self._keys_to_watch:
            self._handler.handle_key_up()

    def start(self) -> None:
        self._listener = keyboard.Listener(on_press=self._on_press, on_release=self._on_release)
        self._listener.start()

    def stop(self) -> None:
        if self._listener:
            self._listener.stop()
            self._listener.join(timeout=1.0)
            self._listener = None

