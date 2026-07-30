"""
Wrapper around Groq's free API for:
- text chat (Ellie's brain)
- vision (understanding photos the user sends)
- transcription (understanding voice messages the user sends)
"""
import logging
from groq import AsyncGroq
import config

logger = logging.getLogger(__name__)

client = AsyncGroq(api_key=config.GROQ_API_KEY)


async def chat_reply(history: list) -> str:
    """history is a list of {"role": "user"/"assistant", "content": str}"""
    try:
        response = await client.chat.completions.create(
            model=config.GROQ_CHAT_MODEL,
            messages=history,
            max_tokens=500,
            temperature=0.9,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.exception("Groq chat call failed")
        raise RuntimeError(f"Ellie's brain hiccupped: {e}") from e


async def describe_image_and_reply(system_prompt: str, image_url: str, caption: str) -> str:
    """Send an image (as a URL Telegram gives us) to the vision model and get Ellie's reply."""
    try:
        response = await client.chat.completions.create(
            model=config.GROQ_VISION_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": caption or "What do you think of this?"},
                        {"type": "image_url", "image_url": {"url": image_url}},
                    ],
                },
            ],
            max_tokens=500,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.exception("Groq vision call failed")
        raise RuntimeError(f"Ellie couldn't look at that image: {e}") from e


async def transcribe_audio(file_path: str) -> str:
    """Transcribe a local audio file using Groq's free Whisper endpoint."""
    try:
        with open(file_path, "rb") as f:
            transcription = await client.audio.transcriptions.create(
                file=(file_path, f.read()),
                model=config.GROQ_WHISPER_MODEL,
            )
        return transcription.text.strip()
    except Exception as e:
        logger.exception("Groq transcription failed")
        raise RuntimeError(f"Ellie couldn't understand that voice note: {e}") from e
