import time
from typing import Optional

from .ring_buffer import RingBuffer


class AsrEngineProtocol:
    def start_session(self, language: str = "ja") -> str: ...
    def push_audio(self, session_id: str, pcm_bytes: bytes) -> None: ...
    def finalize(self, session_id: str, timeout_s: float = 10.0) -> str: ...
    def close_session(self, session_id: str) -> None: ...


class Controller:
    def __init__(
        self,
        engine: AsrEngineProtocol,
        ring: RingBuffer,
        *,
        prebuffer_ms: int = 1000,
        min_capture_ms: int = 1500,
        bytes_per_second: int = 32000,
        language: str = "ja",
    ) -> None:
        self.engine = engine
        self.ring = ring
        self.prebuffer_ms = int(prebuffer_ms)
        self.min_capture_ms = int(min_capture_ms)
        self.bytes_per_second = int(bytes_per_second)
        self.language = language
        self._session: Optional[str] = None
        self._press_at: float = 0.0
        self._recording: bool = False

    def is_recording(self) -> bool:
        return self._recording

    def press(self) -> None:
        if self._recording:
            return
        self._session = self.engine.start_session(language=self.language)
        n = int(self.bytes_per_second * (self.prebuffer_ms / 1000.0))
        if n > 0:
            pre = self.ring.snapshot_tail(n)
            if pre:
                self.engine.push_audio(self._session, pre)
        self._press_at = time.time()
        self._recording = True

    def release(self, *, timeout_s: float = 10.0) -> str:
        if not self._recording or not self._session:
            return ""
        # respect minimum capture if needed (best-effort)
        held_ms = int((time.time() - self._press_at) * 1000)
        if held_ms < self.min_capture_ms:
            time.sleep((self.min_capture_ms - held_ms) / 1000.0)

        text = self.engine.finalize(self._session, timeout_s=timeout_s)
        self.engine.close_session(self._session)
        self._session = None
        self._recording = False
        return text

    def live_push(self, pcm_bytes: bytes) -> None:
        """Push live PCM to the engine if a session is active."""
        if not self._recording or not self._session:
            return
        if not pcm_bytes:
            return
        self.engine.push_audio(self._session, pcm_bytes)
