import os
import sys

# Add api/ directory to path so sibling modules (database, config, etc.) are importable on Vercel
sys.path.insert(0, os.path.dirname(__file__))

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

import database as db
from call_handler import router as call_router

PUBLIC_DIR = os.path.join(os.path.dirname(__file__), "..", "public")


@asynccontextmanager
async def lifespan(app: FastAPI):
    db.init_db()
    yield


app = FastAPI(title="NCPL AI Receptionist", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(call_router, prefix="/voice", tags=["voice"])


# ---------------------------------------------------------------------------
# Frontend
# ---------------------------------------------------------------------------

@app.get("/", include_in_schema=False)
async def dashboard():
    return FileResponse(os.path.join(PUBLIC_DIR, "index.html"))


@app.get("/dashboard.js", include_in_schema=False)
async def serve_js():
    return FileResponse(os.path.join(PUBLIC_DIR, "dashboard.js"))


@app.get("/style.css", include_in_schema=False)
async def serve_css():
    return FileResponse(os.path.join(PUBLIC_DIR, "style.css"))


# ---------------------------------------------------------------------------
# Dashboard API
# ---------------------------------------------------------------------------

@app.get("/api/stats")
async def api_stats():
    return JSONResponse(db.get_stats())


@app.get("/api/calls")
async def api_calls(limit: int = 50):
    return JSONResponse(db.get_recent_calls(limit))


@app.get("/api/calls/{call_sid}")
async def api_call_detail(call_sid: str):
    call = db.get_call(call_sid)
    if not call:
        return JSONResponse({"error": "Not found"}, status_code=404)
    return JSONResponse(call)


@app.get("/api/leads")
async def api_leads(limit: int = 100):
    return JSONResponse(db.get_all_leads(limit))
