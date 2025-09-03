import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from presstalk.engine.fwhisper_engine import FasterWhisperEngine


class FakeBackend:
    def __init__(self):
        self.calls = []

    def transcribe(
        self, pcm_bytes: bytes, *, sample_rate: int, language: str, model: str
    ) -> str:
        self.calls.append((len(pcm_bytes), sample_rate, language, model))
        return f"len={len(pcm_bytes)},sr={sample_rate},lang={language},model={model}"


class TestFasterWhisperEngine(unittest.TestCase):
    def test_flow(self):
        backend = FakeBackend()
        eng = FasterWhisperEngine(
            sample_rate=16000, language="ja", model="small", backend=backend
        )
        sid = eng.start_session()
        eng.push_audio(sid, b"aaaa")
        eng.push_audio(sid, b"bbbbbbbb")
        text = eng.finalize(sid, timeout_s=1)
        self.assertIn("len=12", text)
        self.assertIn("sr=16000", text)
        self.assertIn("lang=ja", text)
        self.assertIn("model=small", text)
        eng.close_session(sid)

    def test_unknown_session_safe(self):
        backend = FakeBackend()
        eng = FasterWhisperEngine(
            sample_rate=16000, language="ja", model="small", backend=backend
        )
        eng.push_audio("nope", b"x")
        out = eng.finalize("nope")
        self.assertEqual(out, "")
        eng.close_session("nope")

    def test_backend_exception_returns_empty(self):
        class BadBackend:
            def transcribe(self, *a, **kw):
                raise RuntimeError("boom")

        eng = FasterWhisperEngine(
            sample_rate=16000, language="ja", model="small", backend=BadBackend()
        )
        sid = eng.start_session()
        eng.push_audio(sid, b"abc")
        out = eng.finalize(sid)
        self.assertEqual(out, "")

    def test_timeout_returns_empty(self):
        import time as _t

        class SlowBackend:
            def transcribe(self, *a, **kw):
                _t.sleep(0.05)  # 50ms
                return "should_not_be_seen"

        eng = FasterWhisperEngine(
            sample_rate=16000, language="ja", model="small", backend=SlowBackend()
        )
        sid = eng.start_session()
        eng.push_audio(sid, b"abcd")
        out = eng.finalize(sid, timeout_s=0.01)  # 10ms timeout
        self.assertEqual(out, "")


if __name__ == "__main__":
    unittest.main()
