import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from presstalk.hotkey import HotkeyHandler


class FakeOrch:
    def __init__(self):
        self.calls = []
    def press(self):
        self.calls.append('press')
    def release(self):
        self.calls.append('release')


class TestHotkey(unittest.TestCase):
    def test_hold_mode(self):
        o = FakeOrch()
        hk = HotkeyHandler(o, mode='hold')
        hk.handle_key_down(); hk.handle_key_down()  # second down ignored
        hk.handle_key_up(); hk.handle_key_up()      # second up ignored
        self.assertEqual(o.calls, ['press', 'release'])

    def test_toggle_mode(self):
        o = FakeOrch()
        hk = HotkeyHandler(o, mode='toggle')
        # first tap -> press
        hk.handle_key_down(); hk.handle_key_up()
        # second tap -> release
        hk.handle_key_down(); hk.handle_key_up()
        # third tap -> press
        hk.handle_key_down(); hk.handle_key_up()
        self.assertEqual(o.calls, ['press', 'release', 'press'])

    def test_hold_bounce_no_double_press(self):
        o = FakeOrch()
        hk = HotkeyHandler(o, mode='hold')
        hk.handle_key_down(); hk.handle_key_down(); hk.handle_key_down()
        self.assertEqual(o.calls, ['press'])
        hk.handle_key_up(); hk.handle_key_up()
        self.assertEqual(o.calls, ['press', 'release'])

    def test_toggle_bounce_no_double_toggle(self):
        o = FakeOrch()
        hk = HotkeyHandler(o, mode='toggle')
        hk.handle_key_down(); hk.handle_key_down(); hk.handle_key_up()
        self.assertEqual(o.calls, ['press'])
        hk.handle_key_down(); hk.handle_key_up()
        self.assertEqual(o.calls, ['press', 'release'])


if __name__ == '__main__':
    unittest.main()
