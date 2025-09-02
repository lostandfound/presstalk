from typing import Optional
import sys


class FasterWhisperBackend:
    """Backend for faster-whisper with preloaded models.

    Note: This module loads models during initialization for better user experience.
    It expects 16kHz mono PCM s16le bytes and returns a concatenated text.
    """

    def __init__(
        self,
        *,
        model: str = "small",
        device: Optional[str] = None,
        compute_type: Optional[str] = None,
        beam_size: int = 1,
        show_progress: bool = False,
    ) -> None:
        self._model_name = model
        self._device = device
        self._compute_type = compute_type
        self._beam_size = int(beam_size)
        self._show_progress = show_progress
        self._model = None
        
        # Load model during initialization instead of lazy loading
        self._ensure_model()

    def _ensure_model(self):
        if self._model is not None:
            return
        
        # Show progress if requested
        if self._show_progress:
            print(f"Loading ASR model ({self._model_name})...", end="", flush=True)
            
        try:
            from faster_whisper import WhisperModel  # type: ignore
        except Exception as e:
            if self._show_progress:
                print(" FAILED")
            raise RuntimeError("faster-whisper is not installed") from e
            
        kwargs = {}
        if self._device:
            kwargs["device"] = self._device
        if self._compute_type:
            kwargs["compute_type"] = self._compute_type
            
        try:
            self._model = WhisperModel(self._model_name, **kwargs)
            if self._show_progress:
                print(" Ready!")
        except Exception as e:
            if self._show_progress:
                print(" FAILED")
            raise RuntimeError(f"Failed to load model '{self._model_name}': {e}") from e

    def transcribe(self, pcm_bytes: bytes, *, sample_rate: int, language: str, model: str) -> str:
        if not pcm_bytes:
            return ""
        # Model is already loaded during initialization
        try:
            import numpy as np  # type: ignore
        except Exception as e:
            raise RuntimeError("numpy is required for PCM conversion") from e

        # Convert s16le bytes to float32 mono in [-1,1]
        audio = np.frombuffer(pcm_bytes, dtype=np.int16).astype(np.float32) / 32768.0
        # Faster-Whisper handles resampling internally if needed, but we feed 16k ideally.
        segments, info = self._model.transcribe(
            audio,
            language=language,
            beam_size=self._beam_size,
        )
        texts = []
        for seg in segments:
            # seg.text usually includes a leading space
            t = getattr(seg, "text", "")
            if t:
                texts.append(t.strip())
        return " ".join(texts).strip()