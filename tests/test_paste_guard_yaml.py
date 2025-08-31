import os
import tempfile
import textwrap
import unittest

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from presstalk.config import Config
from presstalk.paste_macos import insert_text


class TestPasteGuardYaml(unittest.TestCase):
    def _write_yaml(self, content: str) -> str:
        fd, path = tempfile.mkstemp(suffix=".yaml")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(textwrap.dedent(content))
        return path

    def test_paste_blocked_when_guard_true_and_app_matches(self):
        path = self._write_yaml(
            """
            paste_guard: true
            paste_blocklist:
              - Terminal
            """
        )
        try:
            cfg = Config(config_path=path)
            # simulate Terminal as frontmost app; run_cmd returns success (would paste if allowed)
            front = lambda: {"name": "Terminal", "bundle_id": "com.apple.Terminal"}
            run_cmd = lambda cmd: 0
            ok = insert_text("hello", frontmost_getter=front, run_cmd=run_cmd, guard_enabled=cfg.paste_guard, blocklist=cfg.paste_blocklist)
            self.assertFalse(ok)
        finally:
            os.remove(path)

    def test_paste_allowed_when_guard_false(self):
        path = self._write_yaml(
            """
            paste_guard: false
            paste_blocklist: [Terminal]
            """
        )
        try:
            cfg = Config(config_path=path)
            # even if Terminal is frontmost, guard disabled => paste proceeds
            front = lambda: {"name": "Terminal"}
            run_cmd = lambda cmd: 0
            ok = insert_text("hello", frontmost_getter=front, run_cmd=run_cmd, guard_enabled=cfg.paste_guard, blocklist=cfg.paste_blocklist)
            self.assertTrue(ok)
        finally:
            os.remove(path)


if __name__ == '__main__':
    unittest.main()

