import os
import asyncio
import json
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from config import settings
import database as db
from call_handler import router as call_router, get_active_calls


@asynccontextmanager
async def lifespan(app: FastAPI):
    db.init_db()
    os.makedirs(settings.AUDIO_DIR, exist_ok=True)
    yield


app = FastAPI(title="NCPL AI Receptionist", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Twilio voice webhooks
app.include_router(call_router, prefix="/voice", tags=["voice"])

# Serve generated audio files for Twilio to fetch
app.mount("/audio", StaticFiles(directory=settings.AUDIO_DIR), name="audio")

# Serve the frontend dashboard
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")


@app.get("/", include_in_schema=False)
async def serve_dashboard():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))


@app.get("/dashboard.js", include_in_schema=False)
async def serve_js():
    return FileResponse(os.path.join(FRONTEND_DIR, "dashboard.js"))


@app.get("/style.css", include_in_schema=False)
async def serve_css():
    return FileResponse(os.path.join(FRONTEND_DIR, "style.css"))


# ---------------------------------------------------------------------------
# Dashboard API
# ---------------------------------------------------------------------------

@app.get("/api/stats")
async def api_stats():
    stats = db.get_stats()
    stats["active_calls_live"] = len(get_active_calls())
    return JSONResponse(stats)


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


@app.get("/api/active-calls")
async def api_active_calls():
    return JSONResponse(get_active_calls())


@app.get("/api/events")
async def sse_events():
    """Server-Sent Events for real-time dashboard updates."""
    async def event_generator():
        while True:
            try:
                stats = db.get_stats()
                stats["active_calls_live"] = len(get_active_calls())
                active = get_active_calls()
                payload = json.dumps({"stats": stats, "active_calls": active})
                yield f"data: {payload}\n\n"
            except Exception:
                pass
            await asyncio.sleep(3)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
