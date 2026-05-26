from __future__ import annotations

import time
from typing import Protocol

from app.application.session_state import SessionState
from app.domain.entities import ChunkResult, InterpretResult, TranslationResult


class AudioConverter(Protocol):
    def convert_to_wav(self, audio_bytes: bytes) -> bytes:
        ...


class SpeechToTextClient(Protocol):
    async def transcribe(self, wav_bytes: bytes, last_transcript: str | None = None, language: str | None = None) -> ChunkResult:
        ...


class TranslationClient(Protocol):
    async def translate(
        self,
        text: str,
        source_language: str,
        target_language: str,
        entity_memory,
    ) -> TranslationResult:
        ...


class InterpretSession:
    def __init__(
        self,
        audio_converter: AudioConverter,
        stt_client: SpeechToTextClient,
        translation_client: TranslationClient,
    ) -> None:
        self.audio_converter = audio_converter
        self.stt_client = stt_client
        self.translation_client = translation_client

    async def process_audio_chunk(self, session: SessionState, audio_bytes: bytes) -> InterpretResult:
        started = time.perf_counter()
        try:
            wav_bytes = self.audio_converter.convert_to_wav(audio_bytes)
        except Exception as exc:  # noqa: BLE001 - boundary returns structured errors
            return self._error_result(session, started, f"audio_conversion_failed: {exc}")

        chunk = await self.stt_client.transcribe(wav_bytes, session.whisper_prompt(), session.whisper_language_hint())
        if chunk.error:
            return self._error_result(session, started, chunk.error, chunk.language)

        if chunk.is_silent or not chunk.text.strip():
            return InterpretResult(
                original="",
                translated="",
                language=chunk.language,
                latency_ms=self._elapsed_ms(started),
                entities=session.entity_memory.as_dict(),
                is_silent=True,
            )

        session.add_transcript(chunk.text)
        session.entity_memory.update(chunk.text)
        source_language, target_language = session.target_language_for(chunk.language)
        translation = await self.translation_client.translate(
            chunk.text,
            source_language,
            target_language,
            session.entity_memory,
        )

        return InterpretResult(
            original=chunk.text,
            translated=translation.translated,
            language=chunk.language,
            latency_ms=self._elapsed_ms(started),
            entities=session.entity_memory.as_dict(),
            error=translation.error,
            cost={
                "audio_seconds": chunk.duration or 0,
                "input_tokens": translation.input_tokens,
                "output_tokens": translation.output_tokens,
            },
        )

    def _error_result(
        self,
        session: SessionState,
        started: float,
        error: str,
        language: str | None = None,
    ) -> InterpretResult:
        return InterpretResult(
            original="",
            translated="",
            language=language,
            latency_ms=self._elapsed_ms(started),
            entities=session.entity_memory.as_dict(),
            error=error,
        )

    @staticmethod
    def _elapsed_ms(started: float) -> int:
        return int((time.perf_counter() - started) * 1000)
