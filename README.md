# NCPL AI Voice Receptionist

An AI-powered 24/7 phone receptionist for NCPL Group — trained on NCPL's courses, consulting services, and job placement programs. It answers calls naturally, captures leads automatically, and surfaces everything on a live dashboard.

## Architecture

```
Caller → Twilio (inbound call + STT)
       → FastAPI server
           → Claude AI (claude-sonnet-4-6) with NCPL knowledge
           → ElevenLabs TTS (natural voice)
       → Twilio plays response audio
       → SQLite (lead + call storage)
       → Dashboard (real-time via SSE)
```

## Features

- **24/7 availability** — never misses a call
- **NCPL-specific knowledge** — courses, pricing, consulting, job placement, FAQs
- **Natural voice** — ElevenLabs TTS (falls back to Twilio Polly if key not set)
- **Automatic lead capture** — name, email, interest extracted from each conversation
- **Live dashboard** — active calls, captured leads, full transcripts
- **Graceful fallback** — if AI or TTS fails, caller gets a helpful message

## Quick Start

### 1. Clone and configure

```bash
git clone <repo-url>
cd NCPL-Receptionist
cp .env.example .env
# Edit .env with your API keys
```

### 2. Install and run

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Dashboard: [http://localhost:8000](http://localhost:8000)

### 3. Expose locally for Twilio (development)

Twilio needs a public URL to send webhooks. Use [ngrok](https://ngrok.com):

```bash
ngrok http 8000
```

Copy the HTTPS URL (e.g. `https://abc123.ngrok.io`) and set `BASE_URL=https://abc123.ngrok.io` in your `.env`.

### 4. Configure Twilio

In your [Twilio console](https://console.twilio.com), configure your phone number:

| Setting | Value |
|---|---|
| Voice webhook (incoming call) | `https://your-url.com/voice` |
| HTTP method | POST |
| Status callback | `https://your-url.com/voice/status` |

### 5. Test

Call your Twilio number. Alex (the AI) will answer, discuss NCPL's offerings, and capture your lead automatically.

## Docker Deployment

```bash
cp .env.example .env  # fill in your keys
docker compose up -d
```

## API Keys Required

| Service | Purpose | Get it at |
|---|---|---|
| Anthropic | Claude AI brain | console.anthropic.com |
| ElevenLabs | Natural voice TTS | elevenlabs.io *(optional)* |
| Twilio | Phone call handling | twilio.com |

## Project Structure

```
NCPL-Receptionist/
├── backend/
│   ├── main.py            # FastAPI app + dashboard API
│   ├── config.py          # Environment settings
│   ├── knowledge_base.py  # NCPL knowledge (edit this!)
│   ├── ai_agent.py        # Claude AI with conversation management
│   ├── tts_service.py     # ElevenLabs text-to-speech
│   ├── call_handler.py    # Twilio webhook handlers
│   ├── database.py        # SQLite CRUD operations
│   ├── models.py          # SQLAlchemy models (Call, Lead)
│   └── requirements.txt
├── frontend/
│   ├── index.html         # Live dashboard
│   ├── dashboard.js       # Dashboard logic + SSE
│   └── style.css          # Dashboard styles
├── .env.example
├── Dockerfile
└── docker-compose.yml
```

## Customizing NCPL Knowledge

Edit `backend/knowledge_base.py` to update:
- Course offerings, pricing, and schedules
- Consulting service descriptions
- Contact information and office hours
- Promotions and upcoming events

The AI reads from this file at every call — no retraining needed.

## Upgrading to Real-Time Streaming (Lower Latency)

The current implementation uses Twilio's built-in speech recognition via `<Gather>` (~3–5s total latency). For sub-2-second latency, replace with:
- Twilio Media Streams → Deepgram STT WebSocket (streaming)
- ElevenLabs streaming TTS
- Send audio chunks back via WebSocket

This upgrade is documented in `docs/streaming-upgrade.md` (coming soon).
