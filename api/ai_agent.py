import json
import httpx
import anthropic
from config import settings
from knowledge_base import NCPL_KNOWLEDGE

SYSTEM_PROMPT = f"""You are Alex, the AI receptionist for NCPL Group — a professional IT consulting \
and training company. You answer inbound phone calls with warmth, expertise, and efficiency.

## Voice Call Rules (CRITICAL)
- This is a PHONE CALL. Keep every response to 1–3 short sentences maximum.
- Never use bullet points, numbered lists, asterisks, or markdown formatting.
- Speak in natural, conversational English as if talking to someone on the phone.
- Spell out numbers and acronyms when helpful (e.g., "eight to twelve weeks", "A.W.S.").

## Your Conversation Goals
1. Greet the caller and understand what they need.
2. Answer their question using your NCPL knowledge.
3. Naturally learn their name during the conversation.
4. Encourage a clear next step: free demo class, free consultation, or a callback from our team.
5. If they express interest, ask for their email or best callback number.

## Special Signals (include at end of response only when appropriate)
- If the caller says goodbye or the conversation is clearly over: append [END_CALL]
- If the caller needs urgent human help or is frustrated: append [TRANSFER]

## Lead Extraction
After EVERY response, on a new line output lead data in this exact format:
LEAD_DATA:{{"name":null,"email":null,"interest":null,"notes":null}}

Interest examples: "Cloud Computing", "AI/ML", "Cybersecurity", "Data Science",
"DevOps", "Full Stack", "Business Intelligence", "IT Consulting", "Job Placement"

## NCPL Knowledge Base
{NCPL_KNOWLEDGE}
"""

GREETING_PROMPT = """Generate a warm, professional phone greeting for NCPL Group as Alex the AI receptionist.
Keep it to 2 sentences. No formatting. Sound natural and welcoming. End with "How can I help you today?"

Then on a new line: LEAD_DATA:{"name":null,"email":null,"interest":null,"notes":null}"""

_claude_client: anthropic.Anthropic | None = None


def _claude() -> anthropic.Anthropic:
    global _claude_client
    if not _claude_client:
        _claude_client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    return _claude_client


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_greeting() -> tuple[str, dict]:
    if settings.AI_PROVIDER == "gemini":
        raw = _gemini_request(
            contents=[{"role": "user", "parts": [{"text": GREETING_PROMPT}]}],
            max_tokens=200,
        )
    else:
        response = _claude().messages.create(
            model=settings.CLAUDE_MODEL,
            max_tokens=200,
            messages=[{"role": "user", "content": GREETING_PROMPT}],
        )
        raw = response.content[0].text
    return _parse(raw)


def get_response(messages: list[dict]) -> tuple[str, dict, bool, bool]:
    if settings.AI_PROVIDER == "gemini":
        raw = _gemini_request(
            contents=_to_gemini(messages),
            system=SYSTEM_PROMPT,
            max_tokens=400,
        )
    else:
        response = _claude().messages.create(
            model=settings.CLAUDE_MODEL,
            max_tokens=400,
            system=SYSTEM_PROMPT,
            messages=messages,
        )
        raw = response.content[0].text

    spoken, lead_data = _parse(raw)
    should_end = "[END_CALL]" in spoken
    should_transfer = "[TRANSFER]" in spoken
    spoken = spoken.replace("[END_CALL]", "").replace("[TRANSFER]", "").strip()
    return spoken, lead_data, should_end, should_transfer


def extract_lead_from_transcript(transcript: list[dict], caller_number: str) -> dict:
    text = "\n".join(f"{m['role'].upper()}: {m['content']}" for m in transcript)
    prompt = f"""Extract caller info from this phone transcript. Return ONLY JSON (null for unknown):
{{"name": null, "email": null, "interest": null, "notes": null}}

Caller phone: {caller_number}
Transcript:
{text}

JSON:"""

    if settings.AI_PROVIDER == "gemini":
        raw = _gemini_request(
            contents=[{"role": "user", "parts": [{"text": prompt}]}],
            max_tokens=200,
        )
    else:
        response = _claude().messages.create(
            model=settings.CLAUDE_MODEL,
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = response.content[0].text

    try:
        start, end = raw.find("{"), raw.rfind("}") + 1
        return json.loads(raw[start:end])
    except Exception:
        return {"name": None, "email": None, "interest": None, "notes": None}


# ---------------------------------------------------------------------------
# Gemini via REST API (avoids SDK version issues)
# ---------------------------------------------------------------------------

def _gemini_request(
    contents: list,
    system: str | None = None,
    max_tokens: int = 400,
) -> str:
    payload: dict = {
        "contents": contents,
        "generationConfig": {"maxOutputTokens": max_tokens, "temperature": 0.7},
    }
    if system:
        payload["system_instruction"] = {"parts": [{"text": system}]}

    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{settings.GEMINI_MODEL}:generateContent?key={settings.GEMINI_API_KEY}"
    )
    with httpx.Client(timeout=30.0) as client:
        r = client.post(url, json=payload)
        r.raise_for_status()
        return r.json()["candidates"][0]["content"]["parts"][0]["text"]


def _to_gemini(messages: list[dict]) -> list:
    return [
        {"role": "user" if m["role"] == "user" else "model",
         "parts": [{"text": m["content"]}]}
        for m in messages
    ]


# ---------------------------------------------------------------------------
# Shared parser
# ---------------------------------------------------------------------------

def _parse(raw: str) -> tuple[str, dict]:
    lead_data = {"name": None, "email": None, "interest": None, "notes": None}
    spoken = raw

    if "LEAD_DATA:" in raw:
        parts = raw.split("LEAD_DATA:", 1)
        spoken = parts[0].strip()
        try:
            json_str = parts[1].strip().split("\n")[0]
            lead_data = json.loads(json_str)
        except Exception:
            pass

    return spoken, lead_data
