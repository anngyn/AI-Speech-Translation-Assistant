from __future__ import annotations

import os
from io import BytesIO

from dotenv import load_dotenv

from app.domain.entities import ChunkResult


class WhisperClient:
    def __init__(self, model: str = "whisper-1") -> None:
        from openai import AsyncOpenAI

        load_dotenv(override=True)
        self.client = AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_WHISPER_BASE_URL") or "https://api.openai.com/v1",
        )
        self.model = os.getenv("OPENAI_WHISPER_MODEL", model)

    async def transcribe(self, wav_bytes: bytes, last_transcript: str | None = None, language: str | None = None) -> ChunkResult:
        try:
            audio_file = BytesIO(wav_bytes)
            audio_file.name = "chunk.wav"
            response = await self.client.audio.transcriptions.create(
                model=self.model,
                file=audio_file,
                prompt=last_transcript,
                language=language,
                response_format="verbose_json",
            )
            text = (getattr(response, "text", "") or "").strip()
            language = getattr(response, "language", None)
            duration = getattr(response, "duration", None)
            segments = getattr(response, "segments", None) or []
            no_speech = max((getattr(s, "no_speech_prob", 0) or 0 for s in segments), default=0)
            is_silent = not bool(text) or no_speech > 0.6
            return ChunkResult(
                text=text if not is_silent else "",
                language=language,
                duration=float(duration) if duration is not None else None,
                is_silent=is_silent,
            )
        except Exception as exc:  # noqa: BLE001 - provider boundary returns structured errors
            return ChunkResult(error=f"whisper_error: {exc}")
