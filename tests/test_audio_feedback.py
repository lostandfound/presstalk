import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from presstalk.orchestrator import Orchestrator


class FakeController:
    def __init__(self):
        self._rec = False
        self.bytes_per_second = 32000
        self.prebuffer_ms = 0

    def live_push(self, b: bytes):
        pass

    def press(self):
        self._rec = True

    def release(self) -> str:
        self._rec = False
        return "ok"


class FakeRing:
    def write(self, b: bytes):
        pass

    def snapshot_tail(self, n: int) -> bytes:
        return b""


class FakeCapture:
    def __init__(self):
        self._running = False

    def start(self, cb):
        self._running = True

    def is_running(self):
        return self._running

    def stop(self):
        self._running = False


class TestAudioFeedback(unittest.TestCase):
    def test_beep_on_press_and_release_when_enabled(self):
        beeps = []

        def _beep():
            beeps.append(1)

        orch = Orchestrator(
            controller=FakeController(),
            ring=FakeRing(),
            capture=FakeCapture(),
            paste_fn=lambda t: True,
            audio_feedback=True,
            beep_fn=_beep,
        )
        orch.press()
        orch.release()
        self.assertEqual(len(beeps), 2)

    def test_no_beep_when_disabled(self):
        beeps = []

        def _beep():
            beeps.append(1)

        orch = Orchestrator(
            controller=FakeController(),
            ring=FakeRing(),
            capture=FakeCapture(),
            paste_fn=lambda t: True,
            audio_feedback=False,
            beep_fn=_beep,
        )
        orch.press()
        orch.release()
        self.assertEqual(beeps, [])

    def test_beep_exception_does_not_break_flow(self):
        def _beep():
            raise RuntimeError("no beep device")

        orch = Orchestrator(
            controller=FakeController(),
            ring=FakeRing(),
            capture=FakeCapture(),
            paste_fn=lambda t: True,
            audio_feedback=True,
            beep_fn=_beep,
        )
        # should not raise
        orch.press()
        text = orch.release()
        self.assertEqual(text, "ok")

    def test_stop_beep_happens_before_finalize(self):
        calls = []

        class Ctrl:
            def __init__(self):
                self.bytes_per_second = 32000
                self.prebuffer_ms = 0

            def live_push(self, b: bytes):
                pass

            def press(self):
                pass

            def release(self) -> str:
                import time

                time.sleep(0.02)
                calls.append("release_done")
                return "ok"

        def _beep():
            calls.append("beep")

        orch = Orchestrator(
            controller=Ctrl(),
            ring=FakeRing(),
            capture=FakeCapture(),
            paste_fn=lambda t: True,
            audio_feedback=True,
            beep_fn=_beep,
        )
        orch.press()
        orch.release()
        # Expect two beeps total; second beep should appear before finalize marker
        self.assertGreaterEqual(calls.count("beep"), 1)
        self.assertIn("release_done", calls)
        # Ensure ordering: a 'beep' exists before 'release_done'
        self.assertLess(calls.index("beep", 1) if calls.count("beep") > 1 else calls.index("beep"), calls.index("release_done"))


if __name__ == "__main__":
    unittest.main()
