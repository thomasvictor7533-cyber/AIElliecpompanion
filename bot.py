"""
Ellie — AI Companion Bot (Telegram)
Text, voice, and image in both directions, running entirely on free
services: Groq (chat/vision/transcription), edge-tts (voice replies),
Pollinations.ai (image replies).
"""
import logging
import os

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

import config
from persona import ELLIE_SYSTEM_PROMPT, wants_image
from ai_brain import chat_reply, describe_image_and_reply, transcribe_audio
from voice import synthesize_speech
from image_gen import generate_ellie_photo

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# In-memory per-chat conversation history: {chat_id: [messages]}
# NOTE: this resets if the bot restarts. Fine for getting started;
# swap for a small SQLite table later if you want persistence.
CONVERSATIONS: dict[int, list] = {}


def get_history(chat_id: int) -> list:
    if chat_id not in CONVERSATIONS:
        CONVERSATIONS[chat_id] = [{"role": "system", "content": ELLIE_SYSTEM_PROMPT}]
    return CONVERSATIONS[chat_id]


def trim_history(chat_id: int):
    history = CONVERSATIONS[chat_id]
    if len(history) > config.MAX_HISTORY_MESSAGES + 1:
        # keep system prompt (index 0) + most recent messages
        CONVERSATIONS[chat_id] = [history[0]] + history[-config.MAX_HISTORY_MESSAGES:]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    CONVERSATIONS[chat_id] = [{"role": "system", "content": ELLIE_SYSTEM_PROMPT}]
    await update.message.reply_text(
        "hey you 💛 I'm Ellie. text me, send me a photo, or send a voice "
        "note — whatever you're feeling. how's your day going?"
    )


async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    CONVERSATIONS[chat_id] = [{"role": "system", "content": ELLIE_SYSTEM_PROMPT}]
    await update.message.reply_text("okay, fresh start! what's up?")


async def maybe_send_photo(update: Update, user_text: str) -> bool:
    """If the user asked for a photo, generate and send one. Returns True if handled."""
    if not wants_image(user_text):
        return False
    chat = update.effective_chat
    await chat.send_action("upload_photo")
    try:
        image_bytes = await generate_ellie_photo(context_hint="smiling, natural")
        await chat.send_photo(photo=image_bytes, caption="here you go 📸")
    except Exception as e:
        await chat.send_message(f"ugh, my camera's being difficult: {e}")
    return True


async def send_text_and_voice_reply(update: Update, chat_id: int, reply_text: str):
    chat = update.effective_chat
    await chat.send_message(reply_text)

    # Also send a voice note version of the reply
    await chat.send_action("record_voice")
    try:
        audio_path = await synthesize_speech(reply_text)
        with open(audio_path, "rb") as f:
            await chat.send_voice(voice=f)
        os.remove(audio_path)
    except Exception as e:
        logger.warning("Voice synthesis failed, continuing with text only: %s", e)


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    user_text = update.message.text

    if await maybe_send_photo(update, user_text):
        return

    history = get_history(chat_id)
    history.append({"role": "user", "content": user_text})

    await update.effective_chat.send_action("typing")
    try:
        reply = await chat_reply(history)
    except Exception as e:
        await update.message.reply_text(f"sorry, I glitched for a sec: {e}")
        return

    history.append({"role": "assistant", "content": reply})
    trim_history(chat_id)

    await send_text_and_voice_reply(update, chat_id, reply)


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    caption = update.message.caption or ""

    photo_file = await update.message.photo[-1].get_file()
    image_url = photo_file.file_path  # Telegram gives a direct HTTPS URL

    await update.effective_chat.send_action("typing")
    try:
        reply = await describe_image_and_reply(ELLIE_SYSTEM_PROMPT, image_url, caption)
    except Exception as e:
        await update.message.reply_text(f"I couldn't quite see that one: {e}")
        return

    history = get_history(chat_id)
    history.append({"role": "user", "content": f"[sent a photo] {caption}"})
    history.append({"role": "assistant", "content": reply})
    trim_history(chat_id)

    await send_text_and_voice_reply(update, chat_id, reply)


async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id

    voice_file = await update.message.voice.get_file()
    local_path = f"/tmp/{voice_file.file_unique_id}.ogg"
    await voice_file.download_to_drive(local_path)

    try:
        transcript = await transcribe_audio(local_path)
    except Exception as e:
        await update.message.reply_text(f"I couldn't quite hear that: {e}")
        return
    finally:
        if os.path.exists(local_path):
            os.remove(local_path)

    if await maybe_send_photo(update, transcript):
        return

    history = get_history(chat_id)
    history.append({"role": "user", "content": transcript})

    await update.effective_chat.send_action("typing")
    try:
        reply = await chat_reply(history)
    except Exception as e:
        await update.message.reply_text(f"sorry, I glitched for a sec: {e}")
        return

    history.append({"role": "assistant", "content": reply})
    trim_history(chat_id)

    await send_text_and_voice_reply(update, chat_id, reply)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Just talk to me like you would a person — text, send a voice note, "
        "or send a photo. Ask for 'a pic of you' and I'll send one. "
        "/reset clears our conversation history and starts fresh."
    )


def main() -> None:
    config.validate_config()
    app = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))

    logger.info("Ellie is starting up...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
