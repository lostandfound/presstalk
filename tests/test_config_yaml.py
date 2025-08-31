import os
import tempfile
import textwrap
import unittest

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from presstalk.config import Config


class TestConfigYaml(unittest.TestCase):
    def _write_yaml(self, content: str) -> str:
        fd, path = tempfile.mkstemp(suffix=".yaml")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(textwrap.dedent(content))
        return path

    def test_yaml_overrides_defaults(self):
        path = self._write_yaml(
            """
            language: en
            model: base
            sample_rate: 22050
            channels: 1
            prebuffer_ms: 123
            min_capture_ms: 456
            mode: toggle
            hotkey: cmd
            paste_guard: false
            paste_blocklist: [FooApp, com.example.foo]
            """
        )
        try:
            cfg = Config(config_path=path)
            self.assertEqual(cfg.language, "en")
            self.assertEqual(cfg.model, "base")
            self.assertEqual(cfg.sample_rate, 22050)
            self.assertEqual(cfg.channels, 1)
            self.assertEqual(cfg.prebuffer_ms, 123)
            self.assertEqual(cfg.min_capture_ms, 456)
            self.assertEqual(cfg.mode, "toggle")
            self.assertEqual(cfg.hotkey, "cmd")
            self.assertEqual(cfg.paste_guard, False)
            # allow list or string; normalize by converting to list of strings
            bl = cfg.paste_blocklist
            if isinstance(bl, str):
                bl = [s.strip() for s in bl.split(",")]
            self.assertIn("FooApp", bl)
        finally:
            os.remove(path)

    def test_env_overrides_yaml(self):
        path = self._write_yaml(
            """
            language: en
            prebuffer_ms: 50
            """
        )
        try:
            os.environ["PT_LANGUAGE"] = "ja"
            os.environ["PT_PREBUFFER_MS"] = "200"
            cfg = Config(config_path=path)
            self.assertEqual(cfg.language, "ja")
            self.assertEqual(cfg.prebuffer_ms, 200)
        finally:
            os.environ.pop("PT_LANGUAGE", None)
            os.environ.pop("PT_PREBUFFER_MS", None)
            os.remove(path)


if __name__ == '__main__':
    unittest.main()

