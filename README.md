# Ellie — AI Companion Bot (Telegram)

A warm, conversational AI companion that texts, sends/receives voice notes,
and sends/receives photos — built entirely on free services:

| Function | Service | Cost |
|---|---|---|
| Conversation brain | Groq (Llama 3.3 70B) | Free tier |
| Understanding photos you send | Groq vision model | Free tier |
| Understanding voice notes you send | Groq Whisper | Free tier |
| Ellie's spoken voice replies | edge-tts | Free, no key needed |
| Ellie's photo replies | Pollinations.ai | Free, no key needed |
| Hosting | Railway | Free tier |

The only API key you need is a free Groq key — no credit card required.

## Part 1 — Get your keys

1. **Telegram bot token**: message [@BotFather](https://t.me/BotFather) →
   `/newbot` → follow prompts → copy the token.
2. **Groq API key**: go to [console.groq.com/keys](https://console.groq.com/keys)
   (free, no credit card) → create a key → copy it.

## Part 2 — Test locally (optional but recommended)

```bash
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` and paste in your two real keys. Then:

```bash
python bot.py
```

Open your bot in Telegram and send `/start`.

## Part 3 — Push to GitHub

```bash
cd ellie-bot
git init
git add .
git commit -m "Ellie companion bot"
```

Create a new repo on [github.com/new](https://github.com/new), then:

```bash
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git branch -M main
git push -u origin main
```

**Important:** `.env` is in `.gitignore` on purpose — never commit your real
keys to GitHub. Only `.env.example` (with placeholder text) should be pushed.

## Part 4 — Deploy on Railway

1. Go to [railway.app](https://railway.app) → sign in with GitHub.
2. **New Project** → **Deploy from GitHub repo** → pick your Ellie repo.
3. Railway will detect the `Procfile` and run `python bot.py` as a worker.
4. Go to your project's **Variables** tab and add:
   - `TELEGRAM_BOT_TOKEN` = your real token
   - `GROQ_API_KEY` = your real key
   - (optional) any of the other variables from `.env.example`
5. Railway will redeploy automatically. Check the **Deployments → Logs** tab
   for `Ellie is starting up...` to confirm it's running.
6. Message your bot on Telegram — it's now live 24/7.

## Files

| File | Purpose |
|---|---|
| `bot.py` | Main bot: Telegram handlers for text/photo/voice |
| `persona.py` | Ellie's personality, system prompt, appearance description |
| `ai_brain.py` | Groq wrapper: chat, vision, transcription |
| `voice.py` | edge-tts wrapper for Ellie's spoken replies |
| `image_gen.py` | Pollinations.ai wrapper for Ellie's photo replies |
| `config.py` | Loads settings from environment variables |
| `Procfile` | Tells Railway how to run the bot |
| `requirements.txt` | Python dependencies |
| `.env.example` | Template for your secrets (never commit the real `.env`) |

## Customizing Ellie

- **Personality/tone**: edit `ELLIE_SYSTEM_PROMPT` in `persona.py`.
- **Her look in generated photos**: edit `ELLIE_APPEARANCE` in `persona.py`.
- **Her voice**: change `ELLIE_VOICE` in `.env`/Railway Variables. Run
  `edge-tts --list-voices` locally to see all free voice options (many
  languages and accents available).
- **Conversation memory length**: `MAX_HISTORY_MESSAGES` in `.env`.

## Known limitations (being upfront about the free-tier tradeoffs)

- **Conversation history resets** if the bot restarts (Railway redeploys,
  crashes, etc.) since it's stored in memory, not a database. Fine for
  getting started — ask me later if you want it to persist permanently
  (a small SQLite file would do it).
- **Groq's free tier** has rate limits (generous, but not infinite) — under
  very heavy use you may see occasional slowdowns or errors.
- **Railway's free tier** gives limited monthly usage hours/credit. Light
  personal use should fit comfortably; if Ellie gets popular, you may
  eventually need Railway's paid tier (a few dollars/month).
- **edge-tts** is an unofficial wrapper around Microsoft's service — it's
  widely used and reliable, but not officially supported by Microsoft, so
  it could theoretically break if they change something on their end.
