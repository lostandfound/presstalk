import os
import subprocess
import ctypes
from ctypes import wintypes
from typing import Callable, Optional, Tuple, Dict, Sequence, Union
from .paste_common import PasteGuard


def _get_frontmost_app(*, runner: Optional[Callable[[list], Tuple[int, str]]] = None) -> Dict[str, str]:
    """Return {'name': ...} of the foreground process on Windows or empty dict on failure.

    runner is unused on Windows implementation but kept for signature parity/testing.
    """
    try:
        user32 = ctypes.windll.user32  # type: ignore[attr-defined]
        GetForegroundWindow = user32.GetForegroundWindow
        GetWindowThreadProcessId = user32.GetWindowThreadProcessId
        GetForegroundWindow.restype = wintypes.HWND
        GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
        hwnd = GetForegroundWindow()
        pid = wintypes.DWORD(0)
        GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        try:
            out = subprocess.check_output(
                [
                    "powershell",
                    "-NoProfile",
                    "-Command",
                    f"(Get-Process -Id {pid.value}).ProcessName",
                ],
                text=True,
                timeout=1,
            ).strip()
        except Exception:
            out = ""
        return {k: v for k, v in {"name": out}.items() if v}
    except Exception:
        return {}


def insert_text(
    text: str,
    *,
    run_cmd: Optional[Callable[[list], int]] = None,
    frontmost_getter: Optional[Callable[[], Dict[str, str]]] = None,
    guard_enabled: Optional[bool] = None,
    blocklist: Optional[Union[str, Sequence[str]]] = None,
    clipboard_fn: Optional[Callable[[str], bool]] = None,
) -> bool:
    """Insert text at current cursor by clipboard swap + Ctrl+V (Windows).

    - If guard is enabled, block paste when foreground process matches blocklist.
    - `run_cmd` (if provided) is called instead of sending keys via pynput; it should
      return 0 on success.
    - `clipboard_fn` (if provided) is used to set clipboard; otherwise `clip.exe`.
    """
    if text is None:
        return True

    # Paste guard
    try:
        fg = frontmost_getter() if frontmost_getter else _get_frontmost_app()
    except Exception:
        fg = {}
    if PasteGuard.should_block(
        fg,
        guard_enabled=guard_enabled,
        blocklist=blocklist,
        default_blocklist="cmd.exe,powershell.exe,pwsh.exe,WindowsTerminal.exe,wt.exe,conhost.exe",
    ):
        return False

    # Clipboard
    if clipboard_fn is not None:
        try:
            if not clipboard_fn(text):
                return False
        except Exception:
            return False
    else:
        try:
            p = subprocess.Popen(["clip"], stdin=subprocess.PIPE, text=True)
            p.communicate(text, timeout=1)
        except Exception:
            return False

    # Key send: Ctrl+V
    if run_cmd is not None:
        try:
            return run_cmd(["ctrl+v"]) == 0
        except Exception:
            return False

    try:
        from pynput import keyboard  # type: ignore
        kb = keyboard.Controller()
        with kb.pressed(keyboard.Key.ctrl):
            kb.press('v')
            kb.release('v')
        return True
    except Exception:
        return False
