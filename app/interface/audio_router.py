from __future__ import annotations

import json
import tempfile
from dataclasses import asdict
from pathlib import Path

from fastapi import APIRouter, File, UploadFile
from fastapi.responses import StreamingResponse

from app.application.interpret_session import InterpretSession
from app.application.session_state import SessionState
from app.infrastructure.audio_utils import PydubAudioConverter, load_audio_file, slice_audio
from app.infrastructure.claude_client import ClaudeClient
from app.infrastructure.whisper_client import WhisperClient

router = APIRouter()


@router.post("/interpret/file")
async def interpret_file(file: UploadFile = File(...)) -> StreamingResponse:
    temp_path = await _persist_upload(file)
    session = SessionState()
    interpreter = InterpretSession(PydubAudioConverter(), WhisperClient(), ClaudeClient())

    async def events():
        try:
            audio = load_audio_file(temp_path)
            for chunk in slice_audio(audio):
                result = await interpreter.process_audio_chunk(session, chunk)
                yield f"data: {json.dumps(asdict(result), ensure_ascii=False)}\n\n"
            yield "event: done\ndata: {}\n\n"
        finally:
            temp_path.unlink(missing_ok=True)

    return StreamingResponse(events(), media_type="text/event-stream")


async def _persist_upload(file: UploadFile) -> Path:
    suffix = Path(file.filename or "audio").suffix
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await file.read())
        return Path(tmp.name)
