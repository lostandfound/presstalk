import os
import subprocess
from typing import Callable, Optional, Tuple, Dict, Sequence, Union
from .paste_common import PasteGuard


def _get_frontmost_app(*, runner: Optional[Callable[[list], Tuple[int, str]]] = None) -> Dict[str, str]:
    """Best-effort frontmost app for Linux.

    - X11: use xdotool/xprop to get WM_CLASS or window name
    - Wayland (sway/wlroots): use swaymsg to get focused node app_id/name
    Returns {'name': ...} or empty dict.
    """
    def _run_out(cmd: list) -> Tuple[int, str]:
        try:
            out = subprocess.check_output(cmd, text=True)
            return (0, out.strip())
        except Exception:
            return (1, "")

    r = runner or _run_out

    # Try swaymsg (Wayland)
    code, out = r(["swaymsg", "-t", "get_tree"])
    if code == 0 and out:
        try:
            import json
            tree = json.loads(out)
            # Depth-first search for focused node
            stack = [tree]
            while stack:
                node = stack.pop()
                if node.get("focused"):
                    name = node.get("app_id") or node.get("name") or ""
                    if name:
                        return {"name": str(name)}
                for k in ("nodes", "floating_nodes", "windows", "childNodes"):
                    if isinstance(node.get(k), list):
                        stack.extend(node[k])
        except Exception:
            pass

    # X11 via xdotool/xprop
    code, wid = r(["xdotool", "getactivewindow"])
    if code == 0 and wid:
        code, klass = r(["xprop", "-id", wid, "WM_CLASS"])
        if code == 0 and klass:
            # format: WM_CLASS(STRING) = "xxx", "YYY"
            try:
                parts = [p.strip().strip('"') for p in klass.split("=", 1)[1].split(",")]
                for p in parts:
                    if p:
                        return {"name": p}
            except Exception:
                pass
        code, name = r(["xprop", "-id", wid, "_NET_WM_NAME"])
        if code == 0 and name:
            try:
                val = name.split("=", 1)[1].strip().strip('"')
                if val:
                    return {"name": val}
            except Exception:
                pass

    return {}


essential_terminals = (
    "gnome-terminal",
    "org.gnome.Terminal",
    "konsole",
    "xterm",
    "alacritty",
    "kitty",
    "wezterm",
    "terminator",
    "tilix",
    "xfce4-terminal",
    "lxterminal",
    "io.elementary.terminal",
)


def _set_clipboard(text: str) -> bool:
    # Try wl-copy (Wayland)
    try:
        p = subprocess.Popen(["wl-copy"], stdin=subprocess.PIPE, text=True)
        p.communicate(text, timeout=1)
        return True
    except Exception:
        pass
    # Try xclip (X11)
    try:
        p = subprocess.Popen(["xclip", "-selection", "clipboard"], stdin=subprocess.PIPE, text=True)
        p.communicate(text, timeout=1)
        return True
    except Exception:
        pass
    # Try xsel (fallback)
    try:
        p = subprocess.Popen(["xsel", "--clipboard", "--input"], stdin=subprocess.PIPE, text=True)
        p.communicate(text, timeout=1)
        return True
    except Exception:
        pass
    return False


def insert_text(
    text: str,
    *,
    run_cmd: Optional[Callable[[list], int]] = None,
    frontmost_getter: Optional[Callable[[], Dict[str, str]]] = None,
    guard_enabled: Optional[bool] = None,
    blocklist: Optional[Union[str, Sequence[str]]] = None,
    clipboard_fn: Optional[Callable[[str], bool]] = None,
) -> bool:
    """Insert text at current cursor by clipboard swap + paste keystroke (Linux)."""
    if text is None:
        return True

    # Guard
    try:
        fg = frontmost_getter() if frontmost_getter else _get_frontmost_app()
    except Exception:
        fg = {}
    if PasteGuard.should_block(
        fg,
        guard_enabled=guard_enabled,
        blocklist=blocklist,
        default_blocklist=",".join(essential_terminals),
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
        if not _set_clipboard(text):
            return False

    # Paste keystroke
    if run_cmd is not None:
        try:
            return run_cmd(["ctrl+v"]) == 0
        except Exception:
            return False

    # Try pynput
    try:
        from pynput import keyboard  # type: ignore
        kb = keyboard.Controller()
        with kb.pressed(keyboard.Key.ctrl):
            kb.press('v')
            kb.release('v')
        return True
    except Exception:
        pass

    # X11 fallback via xdotool
    try:
        subprocess.run(["xdotool", "key", "--clearmodifiers", "ctrl+v"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception:
        return False
