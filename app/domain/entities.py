from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from app.domain.glossary import GLOSSARY_TERMS


AMOUNT_RE = re.compile(
    r"\b\d+(?:[.,]\d+)?\s*(?:tỷ|ty|triệu|trieu|nghìn|nghin|k|m|bn|million|billion|usd|vnd|%)\b",
    re.IGNORECASE,
)
DATE_RE = re.compile(
    r"\b(?:Q[1-4](?:\s*/\s*\d{4})?|\d{1,2}[/-]\d{1,2}(?:[/-]\d{2,4})?|\d{1,2}[/-]\d{4})\b",
    re.IGNORECASE,
)
NUMBER_RE = re.compile(r"\b\d+(?:[.,]\d+)?%?\b")
PROPER_NOUN_RE = re.compile(
    r"\b(?:[A-ZÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚĂĐĨŨƠƯẠ-Ỵ][\wÀ-ỹ]*(?:\s+[A-ZÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚĂĐĨŨƠƯẠ-Ỵ][\wÀ-ỹ]*){0,3})\b"
)


def _sorted_unique(values: set[str]) -> list[str]:
    return sorted(values, key=lambda value: (value.casefold(), value))


@dataclass
class EntityMemory:
    persons: set[str] = field(default_factory=set)
    amounts: set[str] = field(default_factory=set)
    dates: set[str] = field(default_factory=set)
    org_names: set[str] = field(default_factory=lambda: set(GLOSSARY_TERMS))
    numbers: set[str] = field(default_factory=set)

    def update(self, text: str) -> None:
        if not text:
            return

        self.amounts.update(match.group(0).strip() for match in AMOUNT_RE.finditer(text))
        self.dates.update(match.group(0).strip() for match in DATE_RE.finditer(text))
        self.numbers.update(match.group(0).strip() for match in NUMBER_RE.finditer(text))

        for match in PROPER_NOUN_RE.finditer(text):
            value = match.group(0).strip()
            if value in GLOSSARY_TERMS or value.isupper():
                self.org_names.add(value)
            elif len(value) > 1:
                self.persons.add(value)

    def all_entities(self) -> list[str]:
        merged = set().union(self.persons, self.amounts, self.dates, self.org_names, self.numbers)
        return _sorted_unique(merged)

    def to_prompt_fragment(self) -> str:
        groups = {
            "persons": self.persons,
            "amounts": self.amounts,
            "dates": self.dates,
            "org_names": self.org_names,
            "numbers": self.numbers,
        }
        parts = []
        for name, values in groups.items():
            if values:
                parts.append(f"{name}: {', '.join(_sorted_unique(values))}")
        return "; ".join(parts) if parts else "none"

    def as_dict(self) -> dict[str, list[str]]:
        return {
            "persons": _sorted_unique(self.persons),
            "amounts": _sorted_unique(self.amounts),
            "dates": _sorted_unique(self.dates),
            "org_names": _sorted_unique(self.org_names),
            "numbers": _sorted_unique(self.numbers),
        }


@dataclass(slots=True)
class ChunkResult:
    text: str = ""
    language: str | None = None
    duration: float | None = None
    is_silent: bool = False
    error: str | None = None


@dataclass(slots=True)
class TranslationResult:
    translated: str = ""
    source_language: str | None = None
    target_language: str | None = None
    input_tokens: int = 0
    output_tokens: int = 0
    error: str | None = None


@dataclass(slots=True)
class InterpretResult:
    original: str
    translated: str
    language: str | None
    latency_ms: int
    entities: dict[str, list[str]]
    is_silent: bool = False
    error: str | None = None
    cost: dict[str, Any] = field(default_factory=dict)
