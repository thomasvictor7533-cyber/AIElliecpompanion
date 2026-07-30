"""
Image generation via Pollinations.ai — free, no API key required.
Used when the user asks Ellie to send a photo/selfie.
"""
import logging
import urllib.parse
import httpx
import config
from persona import ELLIE_APPEARANCE

logger = logging.getLogger(__name__)


async def generate_ellie_photo(context_hint: str = "") -> bytes:
    """
    Build a prompt combining Ellie's consistent appearance with any
    context from the conversation (e.g. "at a cafe", "smiling"), and
    return the generated image as bytes.
    """
    prompt = f"{ELLIE_APPEARANCE}, {context_hint}".strip(", ")
    encoded = urllib.parse.quote(prompt)
    url = f"{config.POLLINATIONS_BASE_URL}/{encoded}?width=768&height=1024&nologo=true"

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.content
    except Exception as e:
        logger.exception("Pollinations.ai image generation failed")
        raise RuntimeError(f"Ellie couldn't generate a photo right now: {e}") from e
