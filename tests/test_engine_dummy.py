import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from presstalk.engine.dummy_engine import DummyAsrEngine


class TestDummyEngine(unittest.TestCase):
    def test_flow(self):
        eng = DummyAsrEngine()
        sid = eng.start_session(language="ja")
        self.assertTrue(sid)
        eng.push_audio(sid, b"abc")
        eng.push_audio(sid, b"def")
        text = eng.finalize(sid, timeout_s=0.1)
        self.assertEqual(text, "bytes=6")
        eng.close_session(sid)

    def test_missing_session_is_safe(self):
        eng = DummyAsrEngine()
        # unknown session operations shouldn't raise
        eng.push_audio("x", b"hi")
        txt = eng.finalize("x")
        self.assertEqual(txt, "bytes=0")
        eng.close_session("x")


if __name__ == "__main__":
    unittest.main()
