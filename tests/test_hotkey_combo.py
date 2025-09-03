import os
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from presstalk.config import Config


class FakeKey:
    def __init__(self, name, char=None):
        self._name = name
        self.char = char

    def __repr__(self):
        return f"<Key {self._name}>"


class FakeKeyboard:
    class Key:
        # modifiers (and potential left/right variants)
        ctrl = FakeKey("ctrl")
        ctrl_l = FakeKey("ctrl_l")
        ctrl_r = FakeKey("ctrl_r")
        alt = FakeKey("alt")
        alt_l = FakeKey("alt_l")
        alt_r = FakeKey("alt_r")
        cmd = FakeKey("cmd")
        cmd_l = FakeKey("cmd_l")
        cmd_r = FakeKey("cmd_r")
        shift = FakeKey("shift")
        shift_l = FakeKey("shift_l")
        shift_r = FakeKey("shift_r")
        # common non-modifier keys
        space = FakeKey("space")


class TestHotkeyCombo(unittest.TestCase):
    def test_default_hotkey_ctrl_space(self):
        cfg = Config()
        self.assertEqual(cfg.hotkey, "ctrl+space")

    def test_parse_and_normalize_aliases(self):
        # parse function to be added in hotkey backend module
        from presstalk.hotkey_pynput import normalize_hotkey

        self.assertEqual(normalize_hotkey("Control+Shift+X"), "ctrl+shift+x")
        self.assertEqual(normalize_hotkey("Cmd+Option+V"), "cmd+alt+v")
        self.assertEqual(normalize_hotkey("SHIFT+SPACE"), "shift+space")

    def test_validate_invalid_hotkeys(self):
        from presstalk.hotkey_pynput import validate_hotkey

        # invalid: only modifiers with no primary (except legacy single-modifier allowed)
        self.assertFalse(validate_hotkey("ctrl+alt"))
        # invalid: empty
        self.assertFalse(validate_hotkey(""))
        # valid legacy single modifier
        self.assertTrue(validate_hotkey("ctrl"))
        # valid single non-modifier
        self.assertTrue(validate_hotkey("space"))

    def test_combo_match_shift_space(self):
        # Patch keyboard with fake, and intercept HotkeyHandler calls
        from presstalk import hotkey_pynput as hp

        with mock.patch.object(hp, "keyboard", FakeKeyboard):
            calls = []

            class FakeOrch:
                def press(self):
                    calls.append("press")

                def release(self):
                    calls.append("release")

            runner = hp.GlobalHotkeyRunner(
                FakeOrch(), mode="hold", key_name="shift+space"
            )
            # press shift (no trigger yet)
            runner._on_press(FakeKeyboard.Key.shift)
            self.assertEqual(calls, [])
            # press space (combo completes)
            runner._on_press(FakeKeyboard.Key.space)
            self.assertEqual(calls, ["press"])
            # release space (combo breaks)
            runner._on_release(FakeKeyboard.Key.space)
            self.assertEqual(calls, ["press", "release"])

    def test_combo_match_ctrl_shift_x(self):
        from presstalk import hotkey_pynput as hp

        with mock.patch.object(hp, "keyboard", FakeKeyboard):
            calls = []

            class FakeOrch:
                def press(self):
                    calls.append("press")

                def release(self):
                    calls.append("release")

            runner = hp.GlobalHotkeyRunner(
                FakeOrch(), mode="hold", key_name="ctrl+shift+x"
            )
            # press ctrl and shift first
            runner._on_press(FakeKeyboard.Key.ctrl)
            runner._on_press(FakeKeyboard.Key.shift)
            self.assertEqual(calls, [])
            # press 'x' as a character
            runner._on_press(FakeKey("char", char="x"))
            self.assertEqual(calls, ["press"])  # combo activated
            # release shift breaks combo
            runner._on_release(FakeKeyboard.Key.shift)
            self.assertEqual(calls, ["press", "release"])


if __name__ == "__main__":
    unittest.main()
