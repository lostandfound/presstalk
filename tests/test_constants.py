import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from presstalk.constants import is_env_enabled, FALSY_VALUES  # type: ignore


class TestConstants(unittest.TestCase):
    def test_falsy_values_set(self):
        # Ensure expected canonical strings are represented
        self.assertIn("0", FALSY_VALUES)
        # case-insensitive handling is implemented in is_env_enabled
        self.assertIn("false", [s.lower() for s in FALSY_VALUES])

    def test_is_env_enabled_none_uses_default(self):
        self.assertTrue(is_env_enabled(None, default=True))
        self.assertFalse(is_env_enabled(None, default=False))

    def test_is_env_enabled_recognizes_common_values(self):
        for v in ["0", "false", "False", " FALSE "]:
            self.assertFalse(is_env_enabled(v))
        for v in ["1", "true", "True", "yes", "on", "random", ""]:
            self.assertTrue(is_env_enabled(v))


if __name__ == '__main__':
    unittest.main()

