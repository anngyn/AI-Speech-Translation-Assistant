from __future__ import annotations

import os as _os
_wb = _os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WinGet\Links")
if _os.path.isdir(_wb) and _wb not in _os.environ.get("PATH", ""):
    _os.environ["PATH"] = _wb + _os.pathsep + _os.environ.get("PATH", "")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.interface.audio_router import router as audio_router
from app.interface.ws_handler import router as ws_router

app = FastAPI(title="OnPoint AI Interpreter")
app.state.sessions = {}
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(ws_router)
app.include_router(audio_router)
app.mount("/", StaticFiles(directory="surfaces/browser", html=True), name="browser")
