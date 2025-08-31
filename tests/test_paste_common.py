import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from presstalk.paste_common import PasteGuard  # type: ignore


class TestPasteCommon(unittest.TestCase):
    def setUp(self):
        os.environ.pop("PT_PASTE_GUARD", None)
        os.environ.pop("PT_PASTE_BLOCKLIST", None)

    def tearDown(self):
        os.environ.pop("PT_PASTE_GUARD", None)
        os.environ.pop("PT_PASTE_BLOCKLIST", None)

    def test_guard_disabled_returns_false(self):
        fg = {"name": "Terminal"}
        self.assertFalse(PasteGuard.should_block(fg, guard_enabled=False, default_blocklist="terminal"))

    def test_env_guard_disables(self):
        os.environ["PT_PASTE_GUARD"] = "0"
        fg = {"name": "Terminal"}
        self.assertFalse(PasteGuard.should_block(fg, guard_enabled=None, default_blocklist="terminal"))

    def test_param_blocklist_takes_precedence(self):
        os.environ["PT_PASTE_BLOCKLIST"] = "notepad"
        fg = {"name": "Terminal"}
        # Explicit blocklist should be used instead of env; here it blocks terminal
        self.assertTrue(PasteGuard.should_block(fg, blocklist=["Terminal"], default_blocklist=""))

    def test_env_blocklist_when_param_missing(self):
        os.environ["PT_PASTE_BLOCKLIST"] = "terminal"
        fg = {"name": "Terminal"}
        self.assertTrue(PasteGuard.should_block(fg, blocklist=None, default_blocklist=""))

    def test_default_blocklist_when_no_param_or_env(self):
        fg = {"name": "iTerm2"}
        self.assertTrue(PasteGuard.should_block(fg, blocklist=None, default_blocklist="Terminal,iTerm2"))

    def test_bundle_id_match_on_macos_like(self):
        fg = {"name": "Something", "bundle_id": "com.apple.Terminal"}
        # Should match via bundle_id even if name not matching
        self.assertTrue(PasteGuard.should_block(fg, blocklist=["terminal"], default_blocklist=""))

    def test_string_blocklist_splits_and_normalizes(self):
        fg = {"name": "WindowsTerminal.exe"}
        self.assertTrue(PasteGuard.should_block(fg, blocklist=" powershell.exe , WindowsTerminal.exe ", default_blocklist=""))

    def test_no_fg_info_never_blocks(self):
        self.assertFalse(PasteGuard.should_block({}, blocklist=["anything"], default_blocklist="fallback"))


if __name__ == '__main__':
    unittest.main()

