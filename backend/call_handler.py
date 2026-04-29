"""
Twilio webhook handlers for the NCPL AI Voice Receptionist.

Call flow:
  POST /voice           — new inbound call → play greeting + start Gather
  POST /voice/gather    — user spoke → AI response → play + loop Gather
  POST /voice/status    — call ended → finalize lead & close session
"""
import asyncio
from dataclasses import dataclass, field
from fastapi import APIRouter, Form, Request, Response
from twilio.twiml.voice_response import VoiceResponse, Gather

import ai_agent
import database as db
from tts_service import synthesize, audio_url

router = APIRouter()

# In-memory session store (keyed by CallSid)
_sessions: dict[str, "CallSession"] = {}


@dataclass
class CallSession:
    call_sid: str
    caller_number: str
    messages: list[dict] = field(default_factory=list)
    lead_data: dict = field(default_factory=lambda: {
        "name": None, "email": None, "interest": None, "notes": None
    })
    turn: int = 0


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _twiml_play_and_gather(audio_filename: str, fallback_text: str, action: str) -> str:
    """Return TwiML that plays ElevenLabs audio (or falls back to <Say>) then Gathers."""
    response = VoiceResponse()
    gather = Gather(
        input="speech",
        action=action,
        method="POST",
        speech_timeout="3",
        language="en-US",
        enhanced=True,
    )
    if audio_filename:
        gather.play(audio_url(audio_filename))
    else:
        gather.say(fallback_text, voice="Polly.Joanna")
    response.append(gather)
    # If no speech detected, re-prompt gently
    response.redirect(action + "?SpeechResult=", method="POST")
    return str(response)


def _twiml_say_and_hangup(text: str, audio_filename: str = "") -> str:
    response = VoiceResponse()
    if audio_filename:
        response.play(audio_url(audio_filename))
    else:
        response.say(text, voice="Polly.Joanna")
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
    caller = From
    session = CallSession(call_sid=CallSid, caller_number=caller)
    _sessions[CallSid] = session

    # Persist call record
    db.create_call(CallSid, caller)

    # Generate greeting
    greeting_text, lead_data = ai_agent.get_greeting()
    session.lead_data.update({k: v for k, v in lead_data.items() if v})

    audio_file = f"{CallSid}_0.mp3"
    await synthesize(greeting_text, audio_file)

    session.messages.append({"role": "assistant", "content": greeting_text})
    db.update_call_transcript(CallSid, session.messages)

    gather_url = str(request.url_for("gather"))
    twiml = _twiml_play_and_gather(audio_file, greeting_text, gather_url)
    return Response(content=twiml, media_type="application/xml")


@router.post("/gather")
async def gather(
    request: Request,
    CallSid: str = Form(...),
    SpeechResult: str = Form(default=""),
    Confidence: str = Form(default="0"),
):
    session = _sessions.get(CallSid)
    if not session:
        # Reconstruct minimal session for orphaned callbacks
        session = CallSession(call_sid=CallSid, caller_number="Unknown")
        _sessions[CallSid] = session

    user_speech = SpeechResult.strip()

    # Silent / no speech — re-prompt
    if not user_speech:
        re_prompt = "I'm sorry, I didn't catch that. Could you please repeat what you said?"
        audio_file = f"{CallSid}_silence_{session.turn}.mp3"
        await synthesize(re_prompt, audio_file)
        gather_url = str(request.url_for("gather"))
        return Response(
            content=_twiml_play_and_gather(audio_file, re_prompt, gather_url),
            media_type="application/xml",
        )

    session.turn += 1
    session.messages.append({"role": "user", "content": user_speech})

    # Get AI response
    spoken, lead_data, should_end, should_transfer = ai_agent.get_response(session.messages)
    session.messages.append({"role": "assistant", "content": spoken})

    # Update lead data with any new info
    session.lead_data.update({k: v for k, v in lead_data.items() if v})

    # Persist
    db.update_call_transcript(CallSid, session.messages)
    db.upsert_lead(
        call_sid=CallSid,
        caller_number=session.caller_number,
        **session.lead_data,
    )

    audio_file = f"{CallSid}_{session.turn}.mp3"
    await synthesize(spoken, audio_file)

    if should_end:
        twiml = _twiml_say_and_hangup(spoken, audio_file)
        # Finalize the call
        asyncio.create_task(_finalize_call(session))
        return Response(content=twiml, media_type="application/xml")

    if should_transfer:
        transfer_msg = (
            spoken + " Let me connect you with a team member right away. Please hold."
        )
        transfer_audio = f"{CallSid}_{session.turn}_transfer.mp3"
        await synthesize(transfer_msg, transfer_audio)
        response = VoiceResponse()
        response.play(audio_url(transfer_audio))
        # In production: response.dial("+1XXXXXXXXXX")
        response.say("All agents are currently busy. Someone will call you back shortly.", voice="Polly.Joanna")
        response.hangup()
        asyncio.create_task(_finalize_call(session))
        return Response(content=str(response), media_type="application/xml")

    gather_url = str(request.url_for("gather"))
    twiml = _twiml_play_and_gather(audio_file, spoken, gather_url)
    return Response(content=twiml, media_type="application/xml")


@router.post("/status")
async def call_status(
    CallSid: str = Form(...),
    CallStatus: str = Form(default=""),
    CallDuration: str = Form(default="0"),
):
    session = _sessions.get(CallSid)
    if session:
        asyncio.create_task(_finalize_call(session, int(CallDuration or 0)))
    return Response(content="OK", media_type="text/plain")


# ---------------------------------------------------------------------------
# Background finalization
# ---------------------------------------------------------------------------

async def _finalize_call(session: CallSession, duration: int = 0):
    try:
        # Deep extraction from full transcript
        if session.messages:
            extracted = ai_agent.extract_lead_from_transcript(
                session.messages, session.caller_number
            )
            session.lead_data.update({k: v for k, v in extracted.items() if v})

        db.complete_call(session.call_sid, duration or None)
        db.upsert_lead(
            call_sid=session.call_sid,
            caller_number=session.caller_number,
            **session.lead_data,
        )
    except Exception as exc:
        print(f"[finalize_call] Error for {session.call_sid}: {exc}")
    finally:
        _sessions.pop(session.call_sid, None)


def get_active_calls() -> list[dict]:
    return [
        {
            "call_sid": s.call_sid,
            "caller_number": s.caller_number,
            "turn": s.turn,
            "lead_data": s.lead_data,
        }
        for s in _sessions.values()
    ]
