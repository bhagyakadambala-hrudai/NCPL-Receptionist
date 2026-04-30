"""
Twilio webhook handlers — fully stateless (sessions stored in PostgreSQL).

Call flow:
  POST /voice         → greeting + Gather
  POST /voice/gather  → AI response + Gather (loops)
  POST /voice/status  → finalize lead on hangup
"""
from fastapi import APIRouter, Form, Request, Response
from twilio.twiml.voice_response import VoiceResponse, Gather

import ai_agent
import database as db
from config import settings

router = APIRouter()

_DEFAULT_LEAD = lambda: {"name": None, "email": None, "interest": None, "notes": None}


# ---------------------------------------------------------------------------
# Session helpers (stateless — all state lives in DB)
# ---------------------------------------------------------------------------

def _load_session(call_sid: str) -> dict:
    call = db.get_call(call_sid)
    messages = call.get("transcript", []) if call else []
    lead = db.get_lead_by_call(call_sid)
    return {
        "messages": messages,
        "lead_data": lead if lead else _DEFAULT_LEAD(),
        "caller_number": call.get("caller_number", "Unknown") if call else "Unknown",
    }


# ---------------------------------------------------------------------------
# TwiML builders — use Twilio <Say> (no audio files needed)
# ---------------------------------------------------------------------------

def _say_and_gather(text: str, action: str) -> str:
    response = VoiceResponse()
    gather = Gather(
        input="speech",
        action=action,
        method="POST",
        speech_timeout="3",
        language="en-US",
        enhanced=True,
    )
    gather.say(text, voice=settings.TWILIO_VOICE)
    response.append(gather)
    response.redirect(action + "?SpeechResult=", method="POST")
    return str(response)


def _say_and_hangup(text: str) -> str:
    response = VoiceResponse()
    response.say(text, voice=settings.TWILIO_VOICE)
    response.hangup()
    return str(response)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.post("")
@router.post("/")
async def incoming_call(
    request: Request,
    CallSid: str = Form(...),
    From: str = Form(default="Unknown"),
    To: str = Form(default=""),
):
    db.create_call(CallSid, From)

    greeting, lead_data = ai_agent.get_greeting()
    db.update_call_transcript(CallSid, [{"role": "assistant", "content": greeting}])

    if any(v for v in lead_data.values()):
        db.upsert_lead(CallSid, From, **{k: v for k, v in lead_data.items() if v})

    gather_url = str(request.url_for("gather"))
    return Response(content=_say_and_gather(greeting, gather_url), media_type="application/xml")


@router.post("/gather")
async def gather(
    request: Request,
    CallSid: str = Form(...),
    SpeechResult: str = Form(default=""),
    Confidence: str = Form(default="0"),
):
    gather_url = str(request.url_for("gather"))
    session = _load_session(CallSid)
    messages = session["messages"]
    lead_data = session["lead_data"]
    caller = session["caller_number"]

    user_speech = SpeechResult.strip()

    if not user_speech:
        re_prompt = "I'm sorry, I didn't catch that. Could you please repeat?"
        return Response(content=_say_and_gather(re_prompt, gather_url), media_type="application/xml")

    messages.append({"role": "user", "content": user_speech})
    spoken, new_lead, should_end, should_transfer = ai_agent.get_response(messages)
    messages.append({"role": "assistant", "content": spoken})

    lead_data.update({k: v for k, v in new_lead.items() if v})
    db.update_call_transcript(CallSid, messages)
    db.upsert_lead(call_sid=CallSid, caller_number=caller, **lead_data)

    if should_end:
        return Response(content=_say_and_hangup(spoken), media_type="application/xml")

    if should_transfer:
        full = spoken + " Let me connect you with a team member. Please hold briefly."
        response = VoiceResponse()
        response.say(full, voice=settings.TWILIO_VOICE)
        response.say(
            "All agents are currently busy. Someone will call you back within one hour.",
            voice=settings.TWILIO_VOICE,
        )
        response.hangup()
        return Response(content=str(response), media_type="application/xml")

    return Response(content=_say_and_gather(spoken, gather_url), media_type="application/xml")


@router.post("/status")
async def call_status(
    CallSid: str = Form(...),
    CallStatus: str = Form(default=""),
    CallDuration: str = Form(default="0"),
):
    call = db.get_call(CallSid)
    if call and call.get("status") != "completed":
        db.complete_call(CallSid, int(CallDuration or 0) or None)
        if call.get("transcript"):
            try:
                extracted = ai_agent.extract_lead_from_transcript(
                    call["transcript"], call.get("caller_number", "Unknown")
                )
                db.upsert_lead(
                    call_sid=CallSid,
                    caller_number=call.get("caller_number", "Unknown"),
                    **extracted,
                )
            except Exception as e:
                print(f"[status] lead extraction error: {e}")
    return Response(content="OK", media_type="text/plain")
