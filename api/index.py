import os
import sys

# Add api/ directory to path so sibling modules are importable on Vercel
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

import database as db
from call_handler import router as call_router

# public/ lives inside api/ so it's always co-located with the function on Vercel
PUBLIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "public")


def _serve_file(filename: str, media_type: str):
    path = os.path.join(PUBLIC_DIR, filename)
    if os.path.isfile(path):
        return FileResponse(path, media_type=media_type)
    return HTMLResponse(f"<h3>File not found: {path}</h3><p>PUBLIC_DIR={PUBLIC_DIR}</p>", status_code=404)


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
# Frontend
# ---------------------------------------------------------------------------

@app.get("/", include_in_schema=False)
async def dashboard():
    return _serve_file("index.html", "text/html")


@app.get("/dashboard.js", include_in_schema=False)
async def serve_js():
    return _serve_file("dashboard.js", "application/javascript")


@app.get("/style.css", include_in_schema=False)
async def serve_css():
    return _serve_file("style.css", "text/css")


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
    return JSONResponse({
        "status": "ok",
        "public_dir": PUBLIC_DIR,
        "public_exists": os.path.isdir(PUBLIC_DIR),
        "files": os.listdir(PUBLIC_DIR) if os.path.isdir(PUBLIC_DIR) else [],
        "cwd": os.getcwd(),
    })
