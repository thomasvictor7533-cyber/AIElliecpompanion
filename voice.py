"""
Text-to-speech for Ellie's voice replies, using edge-tts — a free,
no-API-key wrapper around Microsoft Edge's neural voices.
"""
import logging
import uuid
import os
import edge_tts
import config

logger = logging.getLogger(__name__)

TMP_DIR = "/tmp/ellie_voice"
os.makedirs(TMP_DIR, exist_ok=True)


async def synthesize_speech(text: str) -> str:
    """Generate an mp3 file from text and return its path."""
    filename = os.path.join(TMP_DIR, f"{uuid.uuid4().hex}.mp3")
    try:
        communicate = edge_tts.Communicate(text, config.ELLIE_VOICE)
        await communicate.save(filename)
        return filename
    except Exception as e:
        logger.exception("edge-tts synthesis failed")
        raise RuntimeError(f"Ellie's voice generation failed: {e}") from e
