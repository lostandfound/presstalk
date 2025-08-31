import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from presstalk.config import Config


class TestConfig(unittest.TestCase):
    def test_defaults(self):
        cfg = Config()
        self.assertEqual(cfg.language, 'ja')
        self.assertEqual(cfg.sample_rate, 16000)
        self.assertEqual(cfg.channels, 1)
        self.assertEqual(cfg.prebuffer_ms, 1000)
        self.assertEqual(cfg.min_capture_ms, 1800)
        self.assertEqual(cfg.model, 'small')
        self.assertEqual(cfg.bytes_per_second, 32000)

    def test_env_overrides(self):
        os.environ['PT_SAMPLE_RATE'] = '8000'
        os.environ['PT_CHANNELS'] = '2'
        os.environ['PT_MODEL'] = 'base'
        try:
            cfg = Config()
            self.assertEqual(cfg.sample_rate, 8000)
            self.assertEqual(cfg.channels, 2)
            self.assertEqual(cfg.bytes_per_second, 8000*2*2)
            self.assertEqual(cfg.model, 'base')
        finally:
            os.environ.pop('PT_SAMPLE_RATE', None)
            os.environ.pop('PT_CHANNELS', None)
            os.environ.pop('PT_MODEL', None)


if __name__ == '__main__':
    unittest.main()
