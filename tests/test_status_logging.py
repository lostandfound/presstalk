import os
import sys
import time
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from presstalk.cli import _StatusOrch
from presstalk.logger import Logger, set_logger, INFO, QUIET


class FakeOrch:
    def __init__(self, sleep_s=0.02):
        class Ctl:
            def __init__(self):
                self._rec = True

            def is_recording(self):
                return self._rec

        self.controller = Ctl()
        self._sleep = sleep_s

    def press(self):
        return None

    def release(self):
        time.sleep(self._sleep)
        self.controller._rec = False
        return "ok"

    def stats(self):
        return {"bytes": 6400, "duration_s": 0.5, "bytes_per_second": 32000}


class TestStatusLogging(unittest.TestCase):
    def test_logs_include_stats_and_engine_time(self):
        out = []
        lg = Logger(level=INFO, sink=lambda lvl, msg: out.append(msg))
        set_logger(lg)
        orch = _StatusOrch(FakeOrch(sleep_s=0.03))
        orch.press()
        _ = orch.release()
        joined = "\n".join(out)
        self.assertIn("[PT] Stats:", joined)
        self.assertIn("[PT] Engine:", joined)

    def test_quiet_suppresses_status_logs(self):
        out = []
        lg = Logger(level=QUIET, sink=lambda lvl, msg: out.append(msg))
        set_logger(lg)
        orch = _StatusOrch(FakeOrch(sleep_s=0.01))
        orch.press()
        _ = orch.release()
        self.assertEqual(out, [])


if __name__ == "__main__":
    unittest.main()
