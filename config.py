"""
Configuration loader for Ellie — Companion Bot.
All secrets/settings come from environment variables (.env locally,
or Railway's "Variables" tab in production).
"""

import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

# Groq powers both the chat brain and the free Whisper transcription
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_CHAT_MODEL = os.getenv("GROQ_CHAT_MODEL", "openai/gpt-oss-120b")
GROQ_VISION_MODEL = os.getenv("GROQ_VISION_MODEL", "qwen/qwen3.6-27b")
GROQ_WHISPER_MODEL = os.getenv("GROQ_WHISPER_MODEL", "whisper-large-v3-turbo")

# edge-tts voice for Ellie's spoken replies (free, no key needed)
# Full voice list: run `edge-tts --list-voices` after installing
ELLIE_VOICE = os.getenv("ELLIE_VOICE", "en-US-AriaNeural")

# Pollinations.ai needs no API key at all
POLLINATIONS_BASE_URL = "https://image.pollinations.ai/prompt"

MAX_HISTORY_MESSAGES = int(os.getenv("MAX_HISTORY_MESSAGES", "20"))


def validate_config():
    missing = []
    if not TELEGRAM_BOT_TOKEN:
        missing.append("TELEGRAM_BOT_TOKEN")
    if not GROQ_API_KEY:
        missing.append("GROQ_API_KEY")
    if missing:
        raise EnvironmentError(
            f"Missing required config: {', '.join(missing)}. "
            f"Set these in your .env file (local) or Railway Variables tab (prod)."
        )
