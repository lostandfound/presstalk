import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from presstalk.ring_buffer import RingBuffer
from presstalk.controller import Controller


class EngineMock:
    def __init__(self) -> None:
        self.started = []
        self.pushed = []
        self.finalized = []
        self.closed = []

    def start_session(self, language: str = "ja") -> str:
        sid = f"s{len(self.started)}"
        self.started.append((sid, language))
        return sid

    def push_audio(self, session_id: str, pcm_bytes: bytes) -> None:
        self.pushed.append((session_id, pcm_bytes))

    def finalize(self, session_id: str, timeout_s: float = 10.0) -> str:
        self.finalized.append((session_id, timeout_s))
        # return concatenated size as a string for easy assertion
        total = sum(len(b) for sid, b in self.pushed if sid == session_id)
        return f"bytes={total}"

    def close_session(self, session_id: str) -> None:
        self.closed.append(session_id)


class TestController(unittest.TestCase):
    def test_press_release_with_prebuffer(self):
        rb = RingBuffer(16)
        rb.write(b"abcdef")
        eng = EngineMock()
        ctl = Controller(
            eng, rb, prebuffer_ms=1000, min_capture_ms=0, bytes_per_second=1000 * 2
        )  # 1s -> 2000 bytes
        ctl.press()
        self.assertTrue(ctl.is_recording())
        # prebuffer larger than capacity -> entire ring pushed once
        self.assertEqual(len(eng.pushed), 1)
        self.assertEqual(eng.pushed[0][1], b"abcdef")

        text = ctl.release(timeout_s=1)
        self.assertFalse(ctl.is_recording())
        self.assertTrue(text.startswith("bytes="))
        self.assertIn("bytes=6", text)
        self.assertEqual(len(eng.finalized), 1)
        self.assertEqual(len(eng.closed), 1)

    def test_double_press_ignored(self):
        rb = RingBuffer(8)
        rb.write(b"1234")
        eng = EngineMock()
        ctl = Controller(
            eng, rb, prebuffer_ms=0, min_capture_ms=0, bytes_per_second=32000
        )
        ctl.press()
        ctl.press()
        self.assertEqual(len(eng.started), 1)
        ctl.release(timeout_s=0.1)


if __name__ == "__main__":
    unittest.main()
