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


class DummySource:
    def __init__(self, chunks, delay_s=0.0):
        self._chunks = list(chunks)
        self._delay = delay_s
        self.started = False
        self.stopped = False

    def start(self):
        self.started = True

    def read(self, nbytes: int):
        if self._delay:
            time.sleep(self._delay)
        if not self._chunks:
            return None
        return self._chunks.pop(0)

    def stop(self):
        self.stopped = True


class TestOrchestrator(unittest.TestCase):
    def test_press_release_end_to_end_dummy(self):
        ring = RingBuffer(64)
        # preload prebuffer
        ring.write(b"PRE")
        eng = DummyAsrEngine()
        ctl = Controller(eng, ring, prebuffer_ms=1000, min_capture_ms=0, bytes_per_second=100)  # 1s -> 100 bytes
        src = DummySource([b"aa", b"bb", b"cc"], delay_s=0.0)
        cap = PCMCapture(sample_rate=16000, channels=1, chunk_ms=10, source=src)
        pasted = {}
        orch = Orchestrator(controller=ctl, ring=ring, capture=cap, paste_fn=lambda t: pasted.setdefault('t', t) or True)

        orch.press()
        # wait a moment for capture to run
        for _ in range(50):
            if not cap.is_running():
                break
            time.sleep(0.005)
        text = orch.release()
        self.assertTrue(text.startswith('bytes='))
        # PRE(3) + aa bb cc (6) = 9 bytes
        self.assertIn('bytes=9', text)
        self.assertEqual(pasted.get('t'), text)

    def test_stats_include_prebuffer_and_live(self):
        ring = RingBuffer(64)
        ring.write(b"PRE")  # 3 bytes prebuffer
        eng = DummyAsrEngine()
        ctl = Controller(eng, ring, prebuffer_ms=1000, min_capture_ms=0, bytes_per_second=1000*2)
        src = DummySource([b"aa", b"bb"], delay_s=0.0)
        cap = PCMCapture(sample_rate=16000, channels=1, chunk_ms=10, source=src)
        orch = Orchestrator(controller=ctl, ring=ring, capture=cap, paste_fn=lambda t: True)
        orch.press()
        for _ in range(50):
            if not cap.is_running():
                break
            time.sleep(0.005)
        _ = orch.release()
        st = orch.stats()
        # expect 3(prebuffer)+2+2=7 bytes
        self.assertGreaterEqual(st.get('bytes', 0), 7)

    def test_prebuffer_zero_counts_only_live(self):
        ring = RingBuffer(64)
        ring.write(b"PRE")
        eng = DummyAsrEngine()
        ctl = Controller(eng, ring, prebuffer_ms=0, min_capture_ms=0, bytes_per_second=1000*2)
        src = DummySource([b"aa", b"bb"], delay_s=0.0)
        cap = PCMCapture(sample_rate=16000, channels=1, chunk_ms=10, source=src)
        orch = Orchestrator(controller=ctl, ring=ring, capture=cap, paste_fn=lambda t: True)
        orch.press()
        for _ in range(50):
            if not cap.is_running():
                break
            time.sleep(0.005)
        _ = orch.release()
        st = orch.stats()
        # only live 2+2 bytes
        self.assertGreaterEqual(st.get('bytes', 0), 4)
        self.assertLess(st.get('bytes', 0), 7)

    def test_prebuffer_large_uses_ring_size(self):
        ring = RingBuffer(4)
        ring.write(b"ABCD")  # 4 bytes in ring
        eng = DummyAsrEngine()
        # prebuffer_ms translates to a large requested prebuffer; ring caps at 4
        ctl = Controller(eng, ring, prebuffer_ms=2000, min_capture_ms=0, bytes_per_second=1000*2)
        src = DummySource([b"x"], delay_s=0.0)
        cap = PCMCapture(sample_rate=16000, channels=1, chunk_ms=10, source=src)
        orch = Orchestrator(controller=ctl, ring=ring, capture=cap, paste_fn=lambda t: True)
        orch.press()
        for _ in range(50):
            if not cap.is_running():
                break
            time.sleep(0.005)
        _ = orch.release()
        st = orch.stats()
        # at least 4 bytes from ring + 1 live
        self.assertGreaterEqual(st.get('bytes', 0), 5)

    def test_no_paste_on_empty_finalize(self):
        class EmptyEngine(DummyAsrEngine):
            def finalize(self, session_id: str, timeout_s: float = 10.0) -> str:
                return ''
        ring = RingBuffer(32)
        eng = EmptyEngine()
        ctl = Controller(eng, ring, prebuffer_ms=0, min_capture_ms=0, bytes_per_second=32000)
        src = DummySource([b"aa", b"bb"], delay_s=0.0)
        cap = PCMCapture(sample_rate=16000, channels=1, chunk_ms=10, source=src)
        called = { 'cnt': 0 }
        orch = Orchestrator(controller=ctl, ring=ring, capture=cap, paste_fn=lambda t: called.__setitem__('cnt', called['cnt']+1) or True)
        orch.press()
        for _ in range(50):
            if not cap.is_running():
                break
            time.sleep(0.005)
        out = orch.release()
        self.assertEqual(out, '')
        self.assertEqual(called['cnt'], 0)


if __name__ == '__main__':
    unittest.main()
