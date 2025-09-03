import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from presstalk.logger import Logger, QUIET, INFO, DEBUG


class TestLogger(unittest.TestCase):
    def test_info_only_when_level_allows(self):
        out = []
        lg = Logger(level=INFO, sink=lambda lvl, msg: out.append((lvl, msg)))
        lg.info("hello")
        lg.debug("world")
        self.assertEqual(out, [("INFO", "hello")])

    def test_debug_when_debug(self):
        out = []
        lg = Logger(level=DEBUG, sink=lambda lvl, msg: out.append((lvl, msg)))
        lg.info("i")
        lg.debug("d")
        self.assertEqual(out, [("INFO", "i"), ("DEBUG", "d")])

    def test_quiet_suppresses_all(self):
        out = []
        lg = Logger(level=QUIET, sink=lambda lvl, msg: out.append((lvl, msg)))
        lg.info("i")
        lg.debug("d")
        self.assertEqual(out, [])


if __name__ == "__main__":
    unittest.main()
