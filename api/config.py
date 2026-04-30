import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # AI — choose "claude" or "gemini"
    AI_PROVIDER: str = os.getenv("AI_PROVIDER", "claude")

    # Anthropic (used when AI_PROVIDER=claude)
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    CLAUDE_MODEL: str = "claude-sonnet-4-6"

    # Google Gemini (used when AI_PROVIDER=gemini)
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

    # Twilio
    TWILIO_ACCOUNT_SID: str = os.getenv("TWILIO_ACCOUNT_SID", "")
    TWILIO_AUTH_TOKEN: str = os.getenv("TWILIO_AUTH_TOKEN", "")
    TWILIO_PHONE_NUMBER: str = os.getenv("TWILIO_PHONE_NUMBER", "")

    # Server — set to your Vercel URL in production
    BASE_URL: str = os.getenv("BASE_URL", "http://localhost:8000")

    # PostgreSQL — get a free one at neon.tech
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./ncpl.db")

    # Voice for Twilio <Say> (Amazon Polly voices)
    TWILIO_VOICE: str = os.getenv("TWILIO_VOICE", "Polly.Joanna")


settings = Settings()
