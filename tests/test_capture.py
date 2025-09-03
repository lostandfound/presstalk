import os
import sys
import time
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


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
            return None  # finished
        return self._chunks.pop(0)

    def stop(self):
        self.stopped = True


class TestCapture(unittest.TestCase):
    def setUp(self):
        from presstalk.ring_buffer import RingBuffer  # lazy import

        self.RingBuffer = RingBuffer

    def test_emits_all_chunks_and_finishes(self):
        from presstalk.capture import PCMCapture

        src = DummySource([b"aa", b"bb", b"cc"], delay_s=0.0)
        out = []
        cap = PCMCapture(sample_rate=16000, channels=1, chunk_ms=10, source=src)
        cap.start(lambda b: out.append(b))
        # wait for completion
        for _ in range(50):
            if not cap.is_running():
                break
            time.sleep(0.01)
        self.assertFalse(cap.is_running())
        self.assertEqual(out, [b"aa", b"bb", b"cc"])
        self.assertTrue(src.started)
        self.assertTrue(src.stopped)

    def test_stop_early(self):
        from presstalk.capture import PCMCapture

        # many chunks with delay; we will stop early
        src = DummySource([b"x"] * 100, delay_s=0.01)
        out = []
        cap = PCMCapture(sample_rate=16000, channels=1, chunk_ms=10, source=src)
        cap.start(lambda b: out.append(b))
        time.sleep(0.05)
        cap.stop()
        self.assertFalse(cap.is_running())
        # received some but not all
        self.assertGreater(len(out), 0)
        self.assertLess(len(out), 100)

    def test_write_into_ring(self):
        from presstalk.capture import PCMCapture

        ring = self.RingBuffer(16)
        src = DummySource([b"abcd", b"efgh"], delay_s=0.0)
        cap = PCMCapture(sample_rate=16000, channels=1, chunk_ms=10, source=src)
        cap.start(lambda b: ring.write(b))
        for _ in range(50):
            if not cap.is_running():
                break
            time.sleep(0.01)
        self.assertEqual(ring.snapshot_tail(16), b"abcdefgh")


if __name__ == "__main__":
    unittest.main()
