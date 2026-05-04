import os
import sys

# Add api/ directory to path so sibling modules are importable on Vercel
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import JSONResponse, HTMLResponse, Response
from fastapi.middleware.cors import CORSMiddleware

import database as db
from call_handler import router as call_router
from frontend import get_dashboard_html, DASHBOARD_CSS, DASHBOARD_JS


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        db.init_db()
    except Exception as e:
        print(f"[startup] DB init warning: {e}")
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
# Frontend — served from inline Python strings, no file system needed
# ---------------------------------------------------------------------------

@app.get("/", include_in_schema=False)
async def dashboard():
    return HTMLResponse(get_dashboard_html())


@app.get("/style.css", include_in_schema=False)
async def serve_css():
    return Response(content=DASHBOARD_CSS, media_type="text/css")


@app.get("/dashboard.js", include_in_schema=False)
async def serve_js():
    return Response(content=DASHBOARD_JS, media_type="application/javascript")


# ---------------------------------------------------------------------------
# Dashboard API
# ---------------------------------------------------------------------------

@app.get("/api/stats")
async def api_stats():
    try:
        return JSONResponse(db.get_stats())
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.get("/api/calls")
async def api_calls(limit: int = 50):
    try:
        return JSONResponse(db.get_recent_calls(limit))
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.get("/api/calls/{call_sid}")
async def api_call_detail(call_sid: str):
    try:
        call = db.get_call(call_sid)
        if not call:
            return JSONResponse({"error": "Not found"}, status_code=404)
        return JSONResponse(call)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.get("/api/leads")
async def api_leads(limit: int = 100):
    try:
        return JSONResponse(db.get_all_leads(limit))
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.get("/health")
async def health():
    return JSONResponse({"status": "ok", "version": "2.0", "frontend": "inline"})
