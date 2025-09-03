import os
import sys


def beep() -> None:
    """Best-effort cross-platform system beep.

    - Windows: winsound.MessageBeep if available
    - Others: ASCII bell to stdout; fallback to no-op
    """
    try:
        if os.name == "nt":
            try:
                import winsound  # type: ignore

                winsound.MessageBeep()
                return
            except Exception:
                pass
        # Try ASCII bell
        try:
            sys.stdout.write("\a")
            sys.stdout.flush()
        except Exception:
            pass
    except Exception:
        # swallow all
        pass

