from app.application.interpret_session import InterpretSession
from app.application.session_state import SessionState
from app.domain.entities import ChunkResult, TranslationResult


class FakeConverter:
    def convert_to_wav(self, audio_bytes: bytes) -> bytes:
        return b"wav-" + audio_bytes


class FakeStt:
    def __init__(self, text: str):
        self.text = text
        self.last_prompt = None

    async def transcribe(self, wav_bytes: bytes, last_transcript: str | None = None) -> ChunkResult:
        self.last_prompt = last_transcript
        return ChunkResult(text=self.text, language="vi", duration=2.5, is_silent=not bool(self.text))


class FakeTranslator:
    def __init__(self):
        self.calls = 0

    async def translate(self, text, source_language, target_language, entity_memory):
        self.calls += 1
        return TranslationResult(
            translated=f"translated: {text}",
            source_language=source_language,
            target_language=target_language,
            input_tokens=10,
            output_tokens=5,
        )


import asyncio


def test_interpret_session_skips_translation_for_silence():
    translator = FakeTranslator()
    session = InterpretSession(FakeConverter(), FakeStt(""), translator)

    result = asyncio.run(session.process_audio_chunk(SessionState(), b"input"))

    assert result.is_silent is True
    assert translator.calls == 0


def test_interpret_session_updates_memory_and_returns_shape():
    translator = FakeTranslator()
    session = InterpretSession(FakeConverter(), FakeStt("OnPoint đạt 150 tỷ Q1."), translator)

    result = asyncio.run(session.process_audio_chunk(SessionState(), b"input"))

    assert result.original == "OnPoint đạt 150 tỷ Q1."
    assert result.translated.startswith("translated:")
    assert "150 tỷ" in result.entities["amounts"]
    assert result.cost["input_tokens"] == 10
