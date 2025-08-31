from typing import Optional


class RingBuffer:
    """Byte-oriented ring buffer with fixed capacity.

    - write(b): appends bytes, discarding oldest data when exceeding capacity
    - snapshot_tail(n): returns last n bytes (or all if smaller)
    - size(): current number of bytes stored
    - capacity(): fixed maximum number of bytes retained
    """

    def __init__(self, capacity: int) -> None:
        if capacity <= 0:
            raise ValueError("capacity must be > 0")
        self._cap = int(capacity)
        self._buf = bytearray()

    def capacity(self) -> int:
        return self._cap

    def size(self) -> int:
        return len(self._buf)

    def write(self, data: Optional[bytes]) -> None:
        if not data:
            return
        self._buf.extend(data)
        if len(self._buf) > self._cap:
            # trim oldest
            overflow = len(self._buf) - self._cap
            del self._buf[:overflow]

    def snapshot_tail(self, n: int) -> bytes:
        if n <= 0:
            return b""
        if n >= len(self._buf):
            return bytes(self._buf)
        return bytes(self._buf[-n:])

