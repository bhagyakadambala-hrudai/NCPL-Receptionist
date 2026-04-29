from sqlalchemy import Column, String, Integer, DateTime, Text
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime


class Base(DeclarativeBase):
    pass


class Call(Base):
    __tablename__ = "calls"

    id = Column(Integer, primary_key=True, autoincrement=True)
    call_sid = Column(String(64), unique=True, index=True, nullable=False)
    caller_number = Column(String(20), nullable=True)
    status = Column(String(20), default="active")  # active, completed, failed
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    transcript = Column(Text, default="[]")  # JSON array of {role, content} dicts


class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, autoincrement=True)
    call_sid = Column(String(64), index=True, nullable=False)
    caller_number = Column(String(20), nullable=True)
    name = Column(String(100), nullable=True)
    email = Column(String(200), nullable=True)
    interest = Column(String(200), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String(20), default="new")  # new, contacted, converted, lost
