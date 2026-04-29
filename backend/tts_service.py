import os
import httpx
from config import settings

ELEVENLABS_API_URL = "https://api.elevenlabs.io/v1/text-to-speech"


async def synthesize(text: str, filename: str) -> str:
    """
    Synthesize text to speech using ElevenLabs and save as MP3.
    Returns the local file path.
    Falls back to a marker file if ElevenLabs is not configured.
    """
    os.makedirs(settings.AUDIO_DIR, exist_ok=True)
    filepath = os.path.join(settings.AUDIO_DIR, filename)

    if not settings.ELEVENLABS_API_KEY:
        # Return empty path; caller will use Twilio <Say> fallback
        return ""

    url = f"{ELEVENLABS_API_URL}/{settings.ELEVENLABS_VOICE_ID}"
    headers = {
        "xi-api-key": settings.ELEVENLABS_API_KEY,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg",
    }
    payload = {
        "text": text,
        "model_id": "eleven_turbo_v2",
        "voice_settings": {
            "stability": 0.55,
            "similarity_boost": 0.75,
            "style": 0.1,
            "use_speaker_boost": True,
        },
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(url, json=payload, headers=headers)
        response.raise_for_status()
        with open(filepath, "wb") as f:
            f.write(response.content)

    return filepath


def audio_url(filename: str) -> str:
    return f"{settings.BASE_URL}/audio/{filename}"
