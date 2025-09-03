import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from presstalk.config import Config  # type: ignore


class TestConfigRefactorHelpers(unittest.TestCase):
    def setUp(self):
        # clear env before each test
        for k in [
            "PT_LANGUAGE",
            "PT_SAMPLE_RATE",
            "PT_CHANNELS",
            "PT_PREBUFFER_MS",
            "PT_MIN_CAPTURE_MS",
            "PT_MODEL",
            "PT_PASTE_GUARD",
            "PT_PASTE_BLOCKLIST",
            "PT_NO_LOGO",
            "PT_LOGO_STYLE",
        ]:
            os.environ.pop(k, None)

    def tearDown(self):
        for k in [
            "PT_LANGUAGE",
            "PT_SAMPLE_RATE",
            "PT_CHANNELS",
            "PT_PREBUFFER_MS",
            "PT_MIN_CAPTURE_MS",
            "PT_MODEL",
            "PT_PASTE_GUARD",
            "PT_PASTE_BLOCKLIST",
            "PT_NO_LOGO",
            "PT_LOGO_STYLE",
        ]:
            os.environ.pop(k, None)

    def test_get_defaults_os_blocklist(self):
        c = Config()  # will run __post_init__, but we only call helper below
        real = sys.platform
        try:
            sys.platform = "darwin"
            d = c._get_defaults()
            self.assertIn("com.apple.Terminal".lower(), d["paste_blocklist"].lower())
            sys.platform = "win32"
            d = c._get_defaults()
            self.assertIn("powershell.exe", d["paste_blocklist"].lower())
            sys.platform = "linux"
            d = c._get_defaults()
            self.assertTrue(
                any(
                    k in d["paste_blocklist"]
                    for k in ["gnome-terminal", "konsole", "xterm"]
                )
            )
        finally:
            sys.platform = real

    def test_load_env_reads_overrides(self):
        c = Config()
        os.environ["PT_LANGUAGE"] = "en"
        os.environ["PT_SAMPLE_RATE"] = "44100"
        os.environ["PT_CHANNELS"] = "2"
        os.environ["PT_PREBUFFER_MS"] = "250"
        os.environ["PT_MIN_CAPTURE_MS"] = "2000"
        os.environ["PT_MODEL"] = "small"
        os.environ["PT_PASTE_GUARD"] = "0"
        os.environ["PT_PASTE_BLOCKLIST"] = "foo,bar"
        os.environ["PT_NO_LOGO"] = "1"
        os.environ["PT_LOGO_STYLE"] = "simple"
        env = c._load_env()
        self.assertEqual(env["language"], "en")
        self.assertEqual(env["sample_rate"], 44100)
        self.assertEqual(env["channels"], 2)
        self.assertEqual(env["prebuffer_ms"], 250)
        self.assertEqual(env["min_capture_ms"], 2000)
        self.assertEqual(env["model"], "small")
        self.assertEqual(env["paste_guard"], False)
        self.assertEqual(env["paste_blocklist"], "foo,bar")
        self.assertEqual(env["show_logo"], False)
        self.assertEqual(env["logo_style"], "simple")

    def test_apply_overrides_precedence(self):
        c = Config()  # will apply defaults, but we test helper on fresh values
        defaults = {
            "language": "ja",
            "sample_rate": 16000,
            "channels": 1,
            "prebuffer_ms": 1000,
            "min_capture_ms": 1800,
            "model": "small",
            "mode": "hold",
            "hotkey": "ctrl",
            "paste_guard": True,
            "paste_blocklist": "Terminal",
            "show_logo": True,
            "logo_style": "standard",
        }
        yaml_data = {
            "language": "en",
            "prebuffer_ms": 200,
            "paste_guard": False,
            "paste_blocklist": "Xterm",
        }
        env_data = {
            "language": "de",  # env should win
            "min_capture_ms": 2500,
            "paste_guard": True,
            "logo_style": "simple",
        }
        # Reset fields to None to simulate undecided
        c.language = None
        c.sample_rate = None
        c.channels = None
        c.prebuffer_ms = None
        c.min_capture_ms = None
        c.model = None
        c.mode = None
        c.hotkey = None
        c.paste_guard = None
        c.paste_blocklist = None
        c.show_logo = None
        c.logo_style = None
        c._apply_overrides(defaults, yaml_data, env_data)
        self.assertEqual(c.language, "de")
        self.assertEqual(c.prebuffer_ms, 200)
        self.assertEqual(c.min_capture_ms, 2500)
        self.assertEqual(c.paste_guard, True)
        self.assertEqual(c.paste_blocklist, "Xterm")
        self.assertEqual(c.logo_style, "simple")


if __name__ == "__main__":
    unittest.main()
