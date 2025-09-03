from typing import Dict, Optional
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeout


class FasterWhisperEngine:
    """Thin engine wrapper with injectable backend for transcription.

    The backend must provide: transcribe(pcm_bytes, sample_rate, language, model) -> str
    This keeps tests lightweight and decoupled from the heavy dependency.
    """

    def __init__(self, *, sample_rate: int, language: str, model: str, backend) -> None:
        self.sample_rate = int(sample_rate)
        self.language = language
        self.model = model
        self.backend = backend
        self._bufs: Dict[str, bytearray] = {}
        self._seq = 0

    def start_session(self, language: Optional[str] = None) -> str:
        sid = f"fw{self._seq}"
        self._seq += 1
        self._bufs[sid] = bytearray()
        # allow override language per-session if provided
        if language is not None:
            # set per-instance language for simplicity; production could store per-session opts
            self.language = language
        return sid

    def push_audio(self, session_id: str, pcm_bytes: bytes) -> None:
        buf = self._bufs.get(session_id)
        if buf is None:
            return
        if pcm_bytes:
            buf.extend(pcm_bytes)

    def finalize(self, session_id: str, timeout_s: float = 10.0) -> str:
        buf = self._bufs.get(session_id)
        if buf is None:
            return ""
        try:
            with ThreadPoolExecutor(max_workers=1) as ex:
                fut = ex.submit(
                    self.backend.transcribe,
                    bytes(buf),
                    sample_rate=self.sample_rate,
                    language=self.language,
                    model=self.model,
                )
                try:
                    return fut.result(timeout=timeout_s)
                except FutureTimeout:
                    return ""
                except Exception:
                    return ""
        except Exception:
            return ""

    def close_session(self, session_id: str) -> None:
        self._bufs.pop(session_id, None)
