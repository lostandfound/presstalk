import os
import sys
import importlib
import unittest

# Ensure src on path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


def _reload_paste(platform_value: str):
    """Import presstalk.paste with a fake sys.platform, then restore and purge.

    Returns the imported module object while leaving the real environment clean.
    """
    real = sys.platform
    try:
        sys.platform = platform_value
        # Force fresh import
        sys.modules.pop("presstalk.paste", None)
        mod = importlib.import_module("presstalk.paste")
        return mod
    finally:
        # Restore and purge so subsequent imports use the real platform
        sys.platform = real
        sys.modules.pop("presstalk.paste", None)


class TestPasteDispatch(unittest.TestCase):
    def test_dispatch_darwin_uses_macos_impl(self):
        mac_mod = importlib.import_module("presstalk.paste_macos")
        paste = _reload_paste("darwin")
        self.assertIs(paste.insert_text, mac_mod.insert_text)

    def test_dispatch_win32_uses_windows_impl(self):
        win_mod = importlib.import_module("presstalk.paste_windows")
        paste = _reload_paste("win32")
        self.assertIs(paste.insert_text, win_mod.insert_text)

    def test_dispatch_linux_uses_linux_impl(self):
        lin_mod = importlib.import_module("presstalk.paste_linux")
        paste = _reload_paste("linux")
        self.assertIs(paste.insert_text, lin_mod.insert_text)

    def test_dispatch_other_platforms_fallback_to_macos(self):
        mac_mod = importlib.import_module("presstalk.paste_macos")
        paste = _reload_paste("freebsd")
        self.assertIs(paste.insert_text, mac_mod.insert_text)


if __name__ == "__main__":
    unittest.main()
