import os
import sys
import time
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from presstalk.ring_buffer import RingBuffer
from presstalk.controller import Controller
from presstalk.capture import PCMCapture
from presstalk.orchestrator import Orchestrator
from presstalk.engine.dummy_engine import DummyAsrEngine
from presstalk.cli import _StatusOrch


class DummySource:
    def __init__(self, chunks, delay_s=0.0):
        self._chunks = list(chunks)
        self._delay = delay_s
    def start(self):
        pass
    def read(self, nbytes: int):
        if self._delay:
            time.sleep(self._delay)
        if not self._chunks:
            return None
        return self._chunks.pop(0)
    def stop(self):
        pass


class TestStatusAndTiming(unittest.TestCase):
    def test_status_orch_prevents_double_release(self):
        ring = RingBuffer(16)
        eng = DummyAsrEngine()
        ctl = Controller(eng, ring, prebuffer_ms=0, min_capture_ms=0, bytes_per_second=32000)
        src = DummySource([b"aa"], delay_s=0.0)
        cap = PCMCapture(sample_rate=16000, channels=1, chunk_ms=10, source=src)
        calls = {"release": 0}

        class SpyOrch(Orchestrator):
            def release(self) -> str:  # type: ignore[override]
                calls["release"] += 1
                return super().release()

        base = SpyOrch(controller=ctl, ring=ring, capture=cap, paste_fn=lambda t: True)
        orch = _StatusOrch(base)
        orch.press()
        # first release triggers finalizing
        _ = orch.release()
        # immediate second release should be ignored
        _ = orch.release()
        self.assertEqual(calls["release"], 1)
        self.assertFalse(orch.is_finalizing)

    def test_min_capture_enforced(self):
        ring = RingBuffer(8)
        eng = DummyAsrEngine()
        # require at least 80ms capture
        ctl = Controller(eng, ring, prebuffer_ms=0, min_capture_ms=80, bytes_per_second=32000)
        # no live audio
        src = DummySource([], delay_s=0.0)
        cap = PCMCapture(sample_rate=16000, channels=1, chunk_ms=10, source=src)
        orch = Orchestrator(controller=ctl, ring=ring, capture=cap, paste_fn=lambda t: True)
        orch.press()
        t0 = time.time()
        _ = orch.release()
        dt = (time.time() - t0) * 1000.0
        self.assertGreaterEqual(dt, 70.0)  # allow small scheduling jitter


if __name__ == '__main__':
    unittest.main()

