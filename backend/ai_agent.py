import json
import anthropic
from config import settings
from knowledge_base import NCPL_KNOWLEDGE

client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

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
- If the caller says goodbye, thanks and hangs up, or the conversation is clearly over:
  append exactly [END_CALL] at the very end of your response.
- If the caller needs urgent human help or is very frustrated:
  append exactly [TRANSFER] at the very end of your response.

## Lead Extraction
After EVERY response, on a new line starting with LEAD_DATA: output a JSON object with
any information you have captured so far. Use null for unknown fields.
Format: LEAD_DATA:{{"name":null,"email":null,"interest":null,"notes":null}}

Example of interest values: "Cloud Computing", "AI/ML", "Cybersecurity", "Data Science",
"DevOps", "Full Stack", "Business Intelligence", "IT Consulting", "Job Placement", "General Inquiry"

## NCPL Knowledge Base
{NCPL_KNOWLEDGE}
"""

GREETING_PROMPT = """Generate a warm, professional phone greeting for NCPL Group as Alex the AI receptionist.
Keep it to 2 sentences. Do not use any formatting. Sound natural and welcoming.
End with an open question like "How can I help you today?"

After the greeting on a new line write: LEAD_DATA:{{"name":null,"email":null,"interest":null,"notes":null}}"""


def get_greeting() -> tuple[str, dict]:
    response = client.messages.create(
        model=settings.CLAUDE_MODEL,
        max_tokens=200,
        messages=[{"role": "user", "content": GREETING_PROMPT}],
    )
    return _parse_response(response.content[0].text)


def get_response(messages: list[dict]) -> tuple[str, dict, bool, bool]:
    """
    Returns: (spoken_text, lead_data, should_end_call, should_transfer)
    """
    response = client.messages.create(
        model=settings.CLAUDE_MODEL,
        max_tokens=400,
        system=SYSTEM_PROMPT,
        messages=messages,
    )
    raw = response.content[0].text
    spoken, lead_data = _parse_response(raw)

    should_end = "[END_CALL]" in spoken
    should_transfer = "[TRANSFER]" in spoken
    spoken = spoken.replace("[END_CALL]", "").replace("[TRANSFER]", "").strip()

    return spoken, lead_data, should_end, should_transfer


def extract_lead_from_transcript(transcript: list[dict], caller_number: str) -> dict:
    """Run a dedicated extraction pass over the full transcript."""
    transcript_text = "\n".join(
        f"{m['role'].upper()}: {m['content']}" for m in transcript
    )
    prompt = f"""Extract caller information from this phone call transcript.
Return ONLY a JSON object with these fields (use null if not mentioned):
{{"name": null, "email": null, "interest": null, "notes": null}}

The caller's phone number is: {caller_number}

Transcript:
{transcript_text}

JSON:"""

    response = client.messages.create(
        model=settings.CLAUDE_MODEL,
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}],
    )
    try:
        text = response.content[0].text.strip()
        start = text.find("{")
        end = text.rfind("}") + 1
        return json.loads(text[start:end])
    except Exception:
        return {"name": None, "email": None, "interest": None, "notes": None}


def _parse_response(raw: str) -> tuple[str, dict]:
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
