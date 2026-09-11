from __future__ import annotations

import os
from typing import Callable


class TTSEngine:
    """Simple TTS wrapper with an injectable synthesizer for testability."""

    def __init__(self, synthesizer: Callable[[str], bytes] | None = None, voice: str | None = None) -> None:
        self.synthesizer = synthesizer or self._default_synthesizer
        self.voice = voice or os.getenv("TTS_VOICE_ID", "default")

    def _default_synthesizer(self, text: str) -> bytes:
        if not text.strip():
            raise ValueError("Text for TTS cannot be empty.")
        api_key = os.getenv("TTS_API_KEY")
        if not api_key:
            raise RuntimeError("TTS_API_KEY is not set. TTS is disabled until a provider key is configured.")
        raise RuntimeError("No TTS provider implementation configured. Provide a synthesizer callable or configure a provider.")

    def synthesize(self, text: str) -> bytes:
        if not text or not text.strip():
            raise ValueError("Text for TTS cannot be empty.")
        return self.synthesizer(text)
