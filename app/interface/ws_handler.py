from __future__ import annotations

import json
import time
from dataclasses import asdict
from uuid import uuid4

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.application.interpret_session import InterpretSession
from app.application.session_state import SessionState
from app.infrastructure.audio_utils import PydubAudioConverter
from app.infrastructure.claude_client import ClaudeClient
from app.infrastructure.observability import log_session_start, log_session_end, log_chunk
from app.infrastructure.whisper_client import WhisperClient

router = APIRouter()


def create_interpreter() -> InterpretSession:
    return InterpretSession(PydubAudioConverter(), WhisperClient(), ClaudeClient())


@router.websocket("/ws/interpret")
async def interpret_websocket(websocket: WebSocket) -> None:
    await websocket.accept()
    session = SessionState()
    session_id = str(uuid4())
    websocket.app.state.sessions[session_id] = session
    interpreter = create_interpreter()
    webm_header: bytes | None = None

    log_session_start(session_id)
    session_started = time.perf_counter()
    chunk_index = 0
    silent_chunks = 0
    error_chunks = 0
    total_audio_seconds = 0.0
    total_input_tokens = 0
    total_output_tokens = 0

    try:
        while True:
            message = await websocket.receive()
            if "bytes" in message and message["bytes"] is not None:
                chunk = message["bytes"]
                if chunk[:4] == b"\x1a\x45\xdf\xa3":
                    webm_header = chunk
                elif webm_header is not None:
                    chunk = webm_header + chunk
                result = await interpreter.process_audio_chunk(session, chunk)
                await websocket.send_json(asdict(result))

                cost = result.cost or {}
                audio_sec = float(cost.get("audio_seconds") or 0)
                in_tok = int(cost.get("input_tokens") or 0)
                out_tok = int(cost.get("output_tokens") or 0)
                total_audio_seconds += audio_sec
                total_input_tokens += in_tok
                total_output_tokens += out_tok

                if result.error:
                    error_chunks += 1
                    log_chunk(
                        session_id=session_id,
                        chunk_index=chunk_index,
                        total_latency_ms=result.latency_ms,
                        error=result.error,
                    )
                elif not result.is_silent:
                    log_chunk(
                        session_id=session_id,
                        chunk_index=chunk_index,
                        total_latency_ms=result.latency_ms,
                        audio_seconds=audio_sec or None,
                        language=result.language,
                        input_tokens=in_tok or None,
                        output_tokens=out_tok or None,
                        original=result.original,
                        translated=result.translated,
                    )
                else:
                    silent_chunks += 1

                chunk_index += 1

            elif "text" in message and message["text"] is not None:
                await handle_config_frame(session, message["text"])
                await websocket.send_json({"type": "config", "direction": session.direction.value})
    except WebSocketDisconnect:
        pass
    finally:
        websocket.app.state.sessions.pop(session_id, None)
        log_session_end(
            session_id=session_id,
            duration_ms=int((time.perf_counter() - session_started) * 1000),
            total_chunks=chunk_index,
            silent_chunks=silent_chunks,
            error_chunks=error_chunks,
            total_audio_seconds=total_audio_seconds,
            total_input_tokens=total_input_tokens,
            total_output_tokens=total_output_tokens,
        )


async def handle_config_frame(session: SessionState, payload: str) -> None:
    data = json.loads(payload)
    if data.get("action") == "set_language":
        session.set_direction(data.get("direction", "auto"))
