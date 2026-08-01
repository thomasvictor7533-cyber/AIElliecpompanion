"""
Text-to-speech for Ellie's voice replies, using gTTS (Google Translate's
TTS endpoint) — free, no API key needed, and reliable from cloud servers
(unlike edge-tts, which frequently blocks datacenter/cloud IP addresses).
"""
import asyncio
import logging
import os
import uuid

from gtts import gTTS

logger = logging.getLogger(__name__)

TMP_DIR = "/tmp/ellie_voice"
os.makedirs(TMP_DIR, exist_ok=True)


def _synthesize_sync(text: str, filename: str) -> None:
    tts = gTTS(text=text, lang="en")
    tts.save(filename)


async def synthesize_speech(text: str) -> str:
    """Generate an mp3 file from text and return its path."""
    filename = os.path.join(TMP_DIR, f"{uuid.uuid4().hex}.mp3")
    try:
        # gTTS is synchronous/blocking, so run it in a thread to avoid
        # blocking the bot's event loop while it generates audio.
        await asyncio.to_thread(_synthesize_sync, text, filename)
        return filename
    except Exception as e:
        logger.exception("gTTS synthesis failed")
        raise RuntimeError(f"Ellie's voice generation failed: {e}") from e
