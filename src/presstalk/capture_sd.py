import threading
from collections import deque
from typing import Optional


class SoundDeviceSource:
    """PCMSourceProtocol implementation using sounddevice (CoreAudio backend on macOS).

    - Lazily imports sounddevice.
    - Captures mono s16 at given sample_rate.
    - Buffers data in a thread-safe deque for PCMCapture.read to consume.
    """

    def __init__(
        self,
        *,
        sample_rate: int = 16000,
        channels: int = 1,
        frames_per_block: int = 320,
    ) -> None:
        self.sample_rate = int(sample_rate)
        self.channels = int(channels)
        self.frames_per_block = int(frames_per_block)
        self._sd = None
        self._stream = None
        self._buf = deque()
        self._lock = threading.Lock()
        self._bytes_per_frame = self.channels * 2

    def _ensure(self):
        if self._sd is not None:
            return
        try:
            import sounddevice as sd  # type: ignore
        except Exception as e:
            raise RuntimeError("sounddevice is not installed") from e
        self._sd = sd

    def start(self):
        self._ensure()
        sd = self._sd

        def _cb(indata, frames, time_info, status):
            # indata: float32 [-1,1] or int16 depending on dtype; request int16
            with self._lock:
                self._buf.append(bytes(indata))

        self._stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype="int16",
            blocksize=self.frames_per_block,
            callback=_cb,
        )
        self._stream.start()

    def read(self, nbytes: int) -> Optional[bytes]:
        with self._lock:
            if not self._buf:
                return b""
            out = bytearray()
            while self._buf and len(out) < nbytes:
                out.extend(self._buf.popleft())
            return bytes(out)

    def stop(self):
        if self._stream is not None:
            try:
                self._stream.stop()
                self._stream.close()
            finally:
                self._stream = None
