import json
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Call, Lead
from config import settings

# Works with both SQLite (local dev) and PostgreSQL (Vercel/Neon)
if settings.DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False},
    )
else:
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
        pool_size=1,
        max_overflow=0,
    )

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def init_db():
    Base.metadata.create_all(bind=engine)


# --- Call operations ---

def create_call(call_sid: str, caller_number: str):
    with SessionLocal() as db:
        existing = db.query(Call).filter(Call.call_sid == call_sid).first()
        if not existing:
            db.add(Call(call_sid=call_sid, caller_number=caller_number))
            db.commit()


def update_call_transcript(call_sid: str, messages: list):
    with SessionLocal() as db:
        call = db.query(Call).filter(Call.call_sid == call_sid).first()
        if call:
            call.transcript = json.dumps(messages)
            db.commit()


def complete_call(call_sid: str, duration_seconds: int | None = None):
    with SessionLocal() as db:
        call = db.query(Call).filter(Call.call_sid == call_sid).first()
        if call:
            call.status = "completed"
            call.ended_at = datetime.utcnow()
            if duration_seconds:
                call.duration_seconds = duration_seconds
            db.commit()


def get_call(call_sid: str) -> dict | None:
    with SessionLocal() as db:
        c = db.query(Call).filter(Call.call_sid == call_sid).first()
        if not c:
            return None
        return {
            "id": c.id,
            "call_sid": c.call_sid,
            "caller_number": c.caller_number,
            "status": c.status,
            "started_at": c.started_at.isoformat() if c.started_at else None,
            "ended_at": c.ended_at.isoformat() if c.ended_at else None,
            "duration_seconds": c.duration_seconds,
            "transcript": json.loads(c.transcript or "[]"),
        }


def get_recent_calls(limit: int = 50) -> list[dict]:
    with SessionLocal() as db:
        calls = db.query(Call).order_by(Call.started_at.desc()).limit(limit).all()
        return [
            {
                "id": c.id,
                "call_sid": c.call_sid,
                "caller_number": c.caller_number,
                "status": c.status,
                "started_at": c.started_at.isoformat() if c.started_at else None,
                "ended_at": c.ended_at.isoformat() if c.ended_at else None,
                "duration_seconds": c.duration_seconds,
                "transcript": json.loads(c.transcript or "[]"),
            }
            for c in calls
        ]


# --- Lead operations ---

def get_lead_by_call(call_sid: str) -> dict | None:
    with SessionLocal() as db:
        l = db.query(Lead).filter(Lead.call_sid == call_sid).first()
        if not l:
            return None
        return {"name": l.name, "email": l.email, "interest": l.interest, "notes": l.notes}


def upsert_lead(
    call_sid: str,
    caller_number: str,
    name: str | None = None,
    email: str | None = None,
    interest: str | None = None,
    notes: str | None = None,
):
    with SessionLocal() as db:
        lead = db.query(Lead).filter(Lead.call_sid == call_sid).first()
        if lead:
            if name:
                lead.name = name
            if email:
                lead.email = email
            if interest:
                lead.interest = interest
            if notes:
                lead.notes = notes
            db.commit()
        else:
            db.add(Lead(
                call_sid=call_sid,
                caller_number=caller_number,
                name=name,
                email=email,
                interest=interest,
                notes=notes,
            ))
            db.commit()


def get_all_leads(limit: int = 100) -> list[dict]:
    with SessionLocal() as db:
        leads = db.query(Lead).order_by(Lead.created_at.desc()).limit(limit).all()
        return [
            {
                "id": l.id,
                "call_sid": l.call_sid,
                "caller_number": l.caller_number,
                "name": l.name,
                "email": l.email,
                "interest": l.interest,
                "notes": l.notes,
                "created_at": l.created_at.isoformat() if l.created_at else None,
                "status": l.status,
            }
            for l in leads
        ]


def get_stats() -> dict:
    with SessionLocal() as db:
        total_calls = db.query(Call).count()
        active_calls = db.query(Call).filter(Call.status == "active").count()
        total_leads = db.query(Lead).count()
        leads_with_name = db.query(Lead).filter(Lead.name.isnot(None)).count()
        leads_with_email = db.query(Lead).filter(Lead.email.isnot(None)).count()
        return {
            "total_calls": total_calls,
            "active_calls": active_calls,
            "total_leads": total_leads,
            "leads_with_contact": leads_with_email,
            "capture_rate": round(leads_with_name / total_calls * 100, 1) if total_calls else 0,
        }
