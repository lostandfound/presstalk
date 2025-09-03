import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from presstalk.config import Config


class TestPasteGuardDefaults(unittest.TestCase):
    def setUp(self):
        # Ensure env var is not set unless a test sets it
        os.environ.pop("PT_PASTE_BLOCKLIST", None)

    def tearDown(self):
        os.environ.pop("PT_PASTE_BLOCKLIST", None)

    def test_macos_default_blocklist(self):
        real = sys.platform
        try:
            sys.platform = "darwin"
            cfg = Config()
            self.assertIsNotNone(cfg.paste_blocklist)
            bl = cfg.paste_blocklist
            if isinstance(bl, str):
                bl = [s.strip().lower() for s in bl.split(",") if s.strip()]
            self.assertIn("terminal", "".join(bl))
            # ensure typical mac key is present
            joined = ",".join(bl)
            self.assertIn("com.apple.terminal", joined)
        finally:
            sys.platform = real

    def test_windows_default_blocklist(self):
        real = sys.platform
        try:
            sys.platform = "win32"
            cfg = Config()
            bl = cfg.paste_blocklist
            if isinstance(bl, str):
                bl = [s.strip().lower() for s in bl.split(",") if s.strip()]
            joined = ",".join(bl)
            self.assertIn("windowsterminal.exe", joined)
            self.assertIn("powershell.exe", joined)
        finally:
            sys.platform = real

    def test_linux_default_blocklist(self):
        real = sys.platform
        try:
            sys.platform = "linux"
            cfg = Config()
            bl = cfg.paste_blocklist
            if isinstance(bl, str):
                bl = [s.strip().lower() for s in bl.split(",") if s.strip()]
            joined = ",".join(bl)
            # expect a common terminal to be present
            self.assertTrue(
                any(
                    k in joined
                    for k in [
                        "gnome-terminal",
                        "konsole",
                        "xterm",
                        "alacritty",
                        "kitty",
                        "wezterm",
                        "terminator",
                        "tilix",
                    ]
                )
            )
        finally:
            sys.platform = real

    def test_env_overrides_defaults_always(self):
        real = sys.platform
        try:
            sys.platform = "win32"
            os.environ["PT_PASTE_BLOCKLIST"] = "foo,bar"
            cfg = Config()
            bl = cfg.paste_blocklist
            if isinstance(bl, str):
                bl = [s.strip().lower() for s in bl.split(",") if s.strip()]
            self.assertEqual(bl, ["foo", "bar"])
        finally:
            os.environ.pop("PT_PASTE_BLOCKLIST", None)
            sys.platform = real


if __name__ == "__main__":
    unittest.main()
