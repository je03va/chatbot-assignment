from __future__ import annotations

import io
import os
import platform
import shutil
import subprocess
import tempfile
from typing import Callable

from gtts import gTTS

from article_qa.conversation import strip_markdown


def gtts_synthesizer(text: str) -> bytes:
    """Synthesize text using gTTS (Google Text-to-Speech).

    Returns audio in MP3 format as bytes.
    """
    buffer = io.BytesIO()
    gTTS(text=strip_markdown(text), lang="en").write_to_fp(buffer)
    buffer.seek(0)
    return buffer.getvalue()


class TTSEngine:
    """Simple TTS wrapper with an injectable synthesizer for testability."""

    def __init__(self, synthesizer: Callable[[str], bytes] | None = None, voice: str | None = None) -> None:
        self.synthesizer = synthesizer or gtts_synthesizer
        self.voice = voice or os.getenv("TTS_VOICE_ID", "default")

    def synthesize(self, text: str) -> bytes:
        if not text or not text.strip():
            raise ValueError("Text for TTS cannot be empty.")
        return self.synthesizer(strip_markdown(text))

    def play(self, audio: bytes) -> None:
        """Play generated audio without persisting a repo-level output file."""
        if not audio:
            return

        temp_path = None
        try:
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
                temp_file.write(audio)
                temp_path = temp_file.name

            player = self._resolve_player()
            if player is None:
                raise RuntimeError(
                    "No supported audio player found. Install afplay, mpg123, or ffplay for playback."
                )

            subprocess.run(player + [temp_path], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        finally:
            if temp_path:
                try:
                    os.unlink(temp_path)
                except FileNotFoundError:
                    pass

    def _resolve_player(self) -> list[str] | None:
        if platform.system() == "Darwin" and shutil.which("afplay"):
            return ["afplay"]
        if shutil.which("mpg123"):
            return ["mpg123", "-q"]
        if shutil.which("ffplay"):
            return ["ffplay", "-nodisp", "-autoexit"]
        return None
