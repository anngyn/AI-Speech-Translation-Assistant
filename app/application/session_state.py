from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from app.domain.entities import EntityMemory


class LanguageDirection(str, Enum):
    AUTO = "auto"
    EN_VI = "en-vi"
    VI_EN = "vi-en"


@dataclass
class SessionState:
    direction: LanguageDirection = LanguageDirection.AUTO
    entity_memory: EntityMemory = field(default_factory=EntityMemory)
    transcript_tail: list[str] = field(default_factory=list)

    def set_direction(self, direction: str) -> None:
        self.direction = LanguageDirection(direction)

    def add_transcript(self, text: str) -> None:
        clean = text.strip()
        if not clean:
            return
        self.transcript_tail.append(clean)
        self.transcript_tail = self.transcript_tail[-2:]

    def whisper_prompt(self) -> str | None:
        if not self.transcript_tail:
            return None
        return " ".join(self.transcript_tail)

    def whisper_language_hint(self) -> str | None:
        if self.direction == LanguageDirection.EN_VI:
            return "en"
        if self.direction == LanguageDirection.VI_EN:
            return "vi"
        return None

    def target_language_for(self, detected_language: str | None) -> tuple[str, str]:
        if self.direction == LanguageDirection.EN_VI:
            return "English", "Vietnamese"
        if self.direction == LanguageDirection.VI_EN:
            return "Vietnamese", "English"
        if detected_language and detected_language.lower().startswith("vi"):
            return "Vietnamese", "English"
        return "English", "Vietnamese"
