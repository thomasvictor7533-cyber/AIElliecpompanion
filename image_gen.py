"""
Image generation via Pollinations.ai — free, no API key required.
Used when the user asks Ellie to send a photo/selfie.

Each call randomly mixes a look, outfit, setting, and photo style so
Ellie sends varied, cute pictures instead of the same one repeated.
"""
import logging
import random
import urllib.parse
import httpx
import config
from persona import ELLIE_CORE, ELLIE_LOOKS, ELLIE_OUTFITS, ELLIE_SETTINGS, ELLIE_STYLE

logger = logging.getLogger(__name__)


def build_random_prompt(context_hint: str = "") -> str:
    parts = [
        ELLIE_CORE,
        random.choice(ELLIE_LOOKS),
        random.choice(ELLIE_OUTFITS),
        random.choice(ELLIE_SETTINGS),
        random.choice(ELLIE_STYLE),
    ]
    if context_hint:
        parts.append(context_hint)
    return ", ".join(parts)


async def generate_ellie_photo(context_hint: str = "") -> bytes:
    """
    Build a randomized prompt from Ellie's appearance pools (plus any
    context from the conversation, e.g. "happy", "excited") and return
    the generated image as bytes.
    """
    prompt = build_random_prompt(context_hint)
    encoded = urllib.parse.quote(prompt)
    # random seed forces Pollinations to generate a fresh image instead
    # of possibly reusing a cached result for the same prompt text
    seed = random.randint(1, 999999)
    url = (
        f"{config.POLLINATIONS_BASE_URL}/{encoded}"
        f"?width=768&height=1024&nologo=true&seed={seed}"
    )

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.content
    except Exception as e:
        logger.exception("Pollinations.ai image generation failed")
        raise RuntimeError(f"Ellie couldn't generate a photo right now: {e}") from e
