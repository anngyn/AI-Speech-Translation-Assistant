from __future__ import annotations

import json
import logging
import sys
import time
from dataclasses import dataclass, asdict
from typing import Any


def _configure_root() -> logging.Logger:
    logger = logging.getLogger("onpoint")
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        logger.propagate = False
    return logger


_log = _configure_root()
_PREVIEW_LEN = 50


def _emit(level: str, action: str, **fields: Any) -> None:
    record = {
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "lvl": level,
        "action": action,
    }
    record.update({k: v for k, v in fields.items() if v is not None})
    _log.info(json.dumps(record, ensure_ascii=False))


def _preview(text: str | None) -> str | None:
    if not text:
        return None
    return text[:_PREVIEW_LEN] + ("…" if len(text) > _PREVIEW_LEN else "")


def classify_error(error: str) -> str:
    if error.startswith("whisper_error"):
        return "whisper"
    if error.startswith("bedrock_claude_error"):
        return "bedrock"
    if error.startswith("audio_conversion_failed"):
        return "audio"
    return "unknown"


def log_session_start(session_id: str) -> None:
    _emit("INFO", "session.start", session_id=session_id)


def log_chunk(
    *,
    session_id: str,
    chunk_index: int,
    total_latency_ms: int,
    whisper_latency_ms: int | None = None,
    bedrock_latency_ms: int | None = None,
    audio_seconds: float | None = None,
    language: str | None = None,
    no_speech_prob: float | None = None,
    input_tokens: int | None = None,
    output_tokens: int | None = None,
    original: str | None = None,
    translated: str | None = None,
    error: str | None = None,
) -> None:
    if error:
        _emit(
            "ERROR",
            "chunk.error",
            session_id=session_id,
            chunk_index=chunk_index,
            error_type=classify_error(error),
            error=error,
            total_latency_ms=total_latency_ms,
        )
        return

    _emit(
        "INFO",
        "chunk.ok",
        session_id=session_id,
        chunk_index=chunk_index,
        language=language,
        audio_seconds=round(audio_seconds, 2) if audio_seconds else None,
        no_speech_prob=round(no_speech_prob, 3) if no_speech_prob is not None else None,
        whisper_latency_ms=whisper_latency_ms,
        bedrock_latency_ms=bedrock_latency_ms,
        total_latency_ms=total_latency_ms,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        original_preview=_preview(original),
        translated_preview=_preview(translated),
    )


def log_session_end(
    *,
    session_id: str,
    duration_ms: int,
    total_chunks: int,
    silent_chunks: int,
    error_chunks: int,
    total_audio_seconds: float,
    total_input_tokens: int,
    total_output_tokens: int,
) -> None:
    _emit(
        "INFO",
        "session.end",
        session_id=session_id,
        duration_ms=duration_ms,
        total_chunks=total_chunks,
        silent_chunks=silent_chunks,
        error_chunks=error_chunks,
        total_audio_seconds=round(total_audio_seconds, 2),
        total_input_tokens=total_input_tokens,
        total_output_tokens=total_output_tokens,
    )
