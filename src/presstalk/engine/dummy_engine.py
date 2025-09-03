from typing import Dict


class DummyAsrEngine:
    def __init__(self) -> None:
        self._bufs: Dict[str, bytearray] = {}
        self._seq = 0

    def start_session(self, language: str = "ja") -> str:
        sid = f"s{self._seq}"
        self._seq += 1
        self._bufs[sid] = bytearray()
        return sid

    def push_audio(self, session_id: str, pcm_bytes: bytes) -> None:
        buf = self._bufs.get(session_id)
        if buf is None:
            return
        if pcm_bytes:
            buf.extend(pcm_bytes)

    def finalize(self, session_id: str, timeout_s: float = 10.0) -> str:
        buf = self._bufs.get(session_id)
        total = len(buf) if buf is not None else 0
        return f"bytes={total}"

    def close_session(self, session_id: str) -> None:
        self._bufs.pop(session_id, None)
