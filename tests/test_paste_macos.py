import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from presstalk.paste_macos import insert_text


class TestPasteMac(unittest.TestCase):
    def test_insert_text_with_stub_runner(self):
        calls = {}

        def runner(cmd):
            calls["called"] = True
            return 0

        ok = insert_text("hello", run_cmd=runner)
        self.assertTrue(ok)
        self.assertTrue(calls.get("called", False))

    def test_insert_none_returns_true(self):
        self.assertTrue(insert_text(None, run_cmd=lambda _: 0))

    def test_paste_guard_blocks_terminal(self):
        calls = {"run": 0}

        def runner(_cmd):
            calls["run"] += 1
            return 0

        def fg():
            return {"name": "Terminal", "bundle_id": "com.apple.Terminal"}

        ok = insert_text("hello", run_cmd=runner, frontmost_getter=fg)
        self.assertFalse(ok)
        self.assertEqual(calls["run"], 0)

    def test_paste_guard_allows_textedit(self):
        calls = {"run": 0}

        def runner(_cmd):
            calls["run"] += 1
            return 0

        def fg():
            return {"name": "TextEdit", "bundle_id": "com.apple.TextEdit"}

        ok = insert_text("hello", run_cmd=runner, frontmost_getter=fg)
        self.assertTrue(ok)
        self.assertEqual(calls["run"], 1)


if __name__ == "__main__":
    unittest.main()
