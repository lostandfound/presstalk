import os
import subprocess
from typing import Callable, Optional, Tuple, Dict, Sequence, Union


def _get_frontmost_app(*, runner: Optional[Callable[[list], Tuple[int, str]]] = None) -> Dict[str, str]:
    """Return {'name': ..., 'bundle_id': ...} of frontmost app or empty dict on failure.

    runner should execute a command list and return (exit_code, stdout_text).
    """
    def _run(cmd: list) -> Tuple[int, str]:
        try:
            out = subprocess.check_output(cmd, text=True)
            return (0, out.strip())
        except Exception:
            return (1, "")

    runner = runner or _run
    name = ""
    bid = ""
    code, out = runner(["osascript", "-e", 'tell application "System Events" to get name of (first process whose frontmost is true)'])
    if code == 0:
        name = out
    code, out = runner(["osascript", "-e", 'tell application "System Events" to get bundle identifier of (first process whose frontmost is true)'])
    if code == 0:
        bid = out
    return {k: v for k, v in {"name": name, "bundle_id": bid}.items() if v}


def insert_text(
    text: str,
    *,
    run_cmd: Optional[Callable[[list], int]] = None,
    frontmost_getter: Optional[Callable[[], Dict[str, str]]] = None,
    guard_enabled: Optional[bool] = None,
    blocklist: Optional[Union[str, Sequence[str]]] = None,
    clipboard_fn: Optional[Callable[[str], bool]] = None,
) -> bool:
    """Insert text at current cursor by clipboard swap + Cmd+V (macOS).

    For testability, an optional run_cmd can be supplied to execute a command and
    return its exit code. Default uses osascript to send Cmd+V.
    """
    if text is None:
        return True

    # Paste guard: optionally block paste when frontmost app matches blocklist (e.g., Terminal)
    guard = guard_enabled if guard_enabled is not None else (os.getenv("PT_PASTE_GUARD", "1") not in ("0", "false", "False"))
    if guard:
        try:
            fg = frontmost_getter() if frontmost_getter else _get_frontmost_app()
        except Exception:
            fg = {}
        if fg:
            name = (fg.get("name") or "").lower()
            bid = (fg.get("bundle_id") or "").lower()
            if blocklist is None:
                block_env = os.getenv("PT_PASTE_BLOCKLIST", "Terminal,iTerm2,com.apple.Terminal,com.googlecode.iterm2")
                blocks = [s.strip().lower() for s in block_env.split(",") if s.strip()]
            else:
                if isinstance(blocklist, str):
                    blocks = [s.strip().lower() for s in blocklist.split(",") if s.strip()]
                else:
                    blocks = [str(s).strip().lower() for s in blocklist if str(s).strip()]
            targets = [name, bid]
            if any(b and any(t.find(b) != -1 for t in targets if t) for b in blocks):
                return False
    # copy to clipboard
    if clipboard_fn is not None:
        try:
            if not clipboard_fn(text):
                return False
        except Exception:
            return False
    else:
        try:
            p = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE, text=True)
            p.communicate(text, timeout=1)
        except Exception:
            return False

    # simulate Cmd+V via osascript
    if run_cmd is None:
        def _runner(cmd: list) -> int:
            try:
                subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return 0
            except Exception:
                return 1
        run_cmd = _runner

    code = run_cmd(["osascript", "-e", 'tell application "System Events" to keystroke "v" using command down'])
    return code == 0
