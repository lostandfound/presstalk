import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from presstalk.paste_windows import insert_text  # type: ignore


class TestPasteWindows(unittest.TestCase):
    def test_insert_text_with_stub_runner_and_clipboard(self):
        calls = {"run": 0, "clip": 0}

        def runner(cmd):
            calls["run"] += 1
            return 0

        def clipboard_fn(text: str) -> bool:
            calls["clip"] += 1
            return True

        ok = insert_text("hello", run_cmd=runner, clipboard_fn=clipboard_fn)
        self.assertTrue(ok)
        self.assertEqual(calls["clip"], 1)
        self.assertEqual(calls["run"], 1)

    def test_insert_none_returns_true(self):
        self.assertTrue(
            insert_text(None, run_cmd=lambda _: 0, clipboard_fn=lambda t: True)
        )

    def test_paste_guard_blocks_terminal(self):
        calls = {"run": 0, "clip": 0}

        def runner(_cmd):
            calls["run"] += 1
            return 0

        def clipboard_fn(text: str) -> bool:
            calls["clip"] += 1
            return True

        def fg():
            return {"name": "WindowsTerminal.exe"}

        ok = insert_text(
            "hello", run_cmd=runner, frontmost_getter=fg, clipboard_fn=clipboard_fn
        )
        self.assertFalse(ok)
        self.assertEqual(calls["run"], 0)
        self.assertEqual(calls["clip"], 0)

    def test_paste_guard_allows_notepad(self):
        calls = {"run": 0, "clip": 0}

        def runner(_cmd):
            calls["run"] += 1
            return 0

        def clipboard_fn(text: str) -> bool:
            calls["clip"] += 1
            return True

        def fg():
            return {"name": "notepad.exe"}

        ok = insert_text(
            "hello", run_cmd=runner, frontmost_getter=fg, clipboard_fn=clipboard_fn
        )
        self.assertTrue(ok)
        self.assertEqual(calls["run"], 1)
        self.assertEqual(calls["clip"], 1)


if __name__ == "__main__":
    unittest.main()
