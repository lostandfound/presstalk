import time
from typing import Callable

from .controller import Controller
from .ring_buffer import RingBuffer
from .capture import PCMCapture


class Orchestrator:
    """Wires capture → ring + controller live push, handles press/release lifecycle."""

    def __init__(
        self,
        *,
        controller: Controller,
        ring: RingBuffer,
        capture: PCMCapture,
        paste_fn: Callable[[str], bool],
    ) -> None:
        self.controller = controller
        self.ring = ring
        self.capture = capture
        self.paste_fn = paste_fn
        self._started_capture = False
        self._bytes_sent = 0
        self._t0 = 0.0

    def _on_bytes(self, b: bytes):
        if b:
            self.ring.write(b)
            self.controller.live_push(b)
            try:
                self._bytes_sent += len(b)
            except Exception:
                pass

    def press(self):
        # pre-count prebuffer bytes (estimated) for stats
        try:
            n = int(
                self.controller.bytes_per_second
                * (self.controller.prebuffer_ms / 1000.0)
            )
            pre = self.ring.snapshot_tail(n) if n > 0 else b""
            self._bytes_sent = len(pre)
        except Exception:
            self._bytes_sent = 0
        self._t0 = time.time()
        self.controller.press()
        if not self.capture.is_running():
            self.capture.start(self._on_bytes)
            self._started_capture = True

    def release(self) -> str:
        text = self.controller.release()
        if self._started_capture:
            self.capture.stop()
            self._started_capture = False
        if text:
            self.paste_fn(text)
        return text

    def stats(self) -> dict:
        dur = max(0.0, time.time() - self._t0) if self._t0 else 0.0
        try:
            bps = int(self.controller.bytes_per_second)
        except Exception:
            bps = 32000
        return {
            "bytes": int(self._bytes_sent),
            "duration_s": dur,
            "bytes_per_second": bps,
        }
