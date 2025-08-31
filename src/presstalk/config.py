import os
from dataclasses import dataclass


@dataclass
class Config:
    language: str = None
    sample_rate: int = None
    channels: int = None
    prebuffer_ms: int = None
    min_capture_ms: int = None
    model: str = None

    def __post_init__(self):
        self.language = self.language or os.getenv("PT_LANGUAGE", "ja")
        self.sample_rate = int(self.sample_rate or os.getenv("PT_SAMPLE_RATE", "16000"))
        self.channels = int(self.channels or os.getenv("PT_CHANNELS", "1"))
        self.prebuffer_ms = int(self.prebuffer_ms or os.getenv("PT_PREBUFFER_MS", "1000"))
        self.min_capture_ms = int(self.min_capture_ms or os.getenv("PT_MIN_CAPTURE_MS", "1800"))
        self.model = self.model or os.getenv("PT_MODEL", "small")

    @property
    def bytes_per_second(self) -> int:
        return self.sample_rate * self.channels * 2
