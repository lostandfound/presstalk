import io
import os
import sys
import tempfile
import textwrap
import unittest
from types import SimpleNamespace
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import presstalk.cli as cli  # type: ignore
from presstalk.config import Config


class TestCliConfig(unittest.TestCase):
    def _tmp_yaml(self, content: str = "") -> str:
        fd, path = tempfile.mkstemp(suffix=".yaml")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(textwrap.dedent(content))
        return path

    def test_config_show_prints_values(self):
        path = self._tmp_yaml(
            """
            language: en
            model: base
            hotkey: ctrl+space
            audio_feedback: true
            """
        )
        try:
            args = SimpleNamespace(cmd="config", config=path, show=True)
            buf = io.StringIO()
            with mock.patch("sys.stdout", buf):
                rc = cli._run_config(args)
            out = buf.getvalue()
            self.assertEqual(rc, 0)
            self.assertIn("Current hotkey:", out)
            self.assertIn("ctrl+space", out)
            self.assertIn("language:", out)
            self.assertIn("model:", out)
            self.assertIn("audio feedback:", out.lower())
        finally:
            os.remove(path)

    def test_config_interactive_updates_and_saves(self):
        path = self._tmp_yaml(
            """
            language: ja
            model: small
            hotkey: ctrl+space
            audio_feedback: true
            """
        )
        try:
            # Provide new values and accept save
            inputs = [
                "ctrl+shift+x",  # new hotkey
                "en",            # language
                "base",          # model
                "n",             # audio feedback disabled
                "y",             # save
            ]
            args = SimpleNamespace(cmd="config", config=path, show=False)
            with mock.patch("builtins.input", side_effect=inputs):
                rc = cli._run_config(args)
            self.assertEqual(rc, 0)
            # Reload and verify file has updated values
            cfg = Config(config_path=path)
            self.assertEqual(cfg.hotkey, "ctrl+shift+x")
            self.assertEqual(cfg.language, "en")
            self.assertEqual(cfg.model, "base")
            self.assertEqual(cfg.audio_feedback, False)
        finally:
            os.remove(path)

    def test_invalid_hotkey_is_handled(self):
        path = self._tmp_yaml("language: ja\nmodel: small\nhotkey: ctrl+space\n")
        try:
            # invalid hotkey then empty to keep current, then save
            inputs = [
                "ctrl+alt",  # invalid (no primary)
                "",          # keep current
                "",          # language keep
                "",          # model keep
                "",          # audio feedback keep default prompt
                "y",         # save
            ]
            args = SimpleNamespace(cmd="config", config=path, show=False)
            with mock.patch("builtins.input", side_effect=inputs):
                rc = cli._run_config(args)
            self.assertEqual(rc, 0)
            cfg = Config(config_path=path)
            self.assertEqual(cfg.hotkey, "ctrl+space")  # unchanged
        finally:
            os.remove(path)


if __name__ == "__main__":
    unittest.main()

