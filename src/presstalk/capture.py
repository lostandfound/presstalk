import threading
import time
from typing import Callable, Optional


class PCMSourceProtocol:
    def start(self) -> None: ...
    def read(
        self, nbytes: int
    ) -> Optional[bytes]: ...  # None => finished, b"" => no data yet
    def stop(self) -> None: ...


class PCMCapture:
    """Pull-based PCM capture loop using an abstract source.

    - sample_rate/channels determine bytes_per_second (s16le)
    - chunk_ms controls nominal read size per iteration
    - source implements start/read/stop, making this unit-testable without devices
    """

    def __init__(
        self,
        *,
        sample_rate: int,
        channels: int,
        chunk_ms: int,
        source: PCMSourceProtocol,
    ) -> None:
        self.sample_rate = int(sample_rate)
        self.channels = int(channels)
        self.chunk_ms = int(chunk_ms)
        self.source = source
        self._thread: Optional[threading.Thread] = None
        self._stop = threading.Event()
        self._running = threading.Event()

    def bytes_per_second(self) -> int:
        return self.sample_rate * self.channels * 2

    def is_running(self) -> bool:
        return self._running.is_set()

    def start(self, on_bytes: Callable[[bytes], None]) -> None:
        if self._thread is not None:
            return
        self._stop.clear()

        def _loop():
            try:
                self.source.start()
            except Exception:
                pass
            self._running.set()
            nbytes = max(1, int(self.bytes_per_second() * (self.chunk_ms / 1000.0)))
            try:
                while not self._stop.is_set():
                    try:
                        data = self.source.read(nbytes)
                    except Exception:
                        break
                    if data is None:
                        break
                    if not data:
                        time.sleep(0.005)
                        continue
                    try:
                        on_bytes(data)
                    except Exception:
                        # swallow callback errors
                        pass
            finally:
                try:
                    self.source.stop()
                except Exception:
                    pass
                self._running.clear()

        self._thread = threading.Thread(target=_loop, name="pcm-capture", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        t = self._thread
        if t is not None:
            t.join(timeout=1.0)
        self._thread = None
