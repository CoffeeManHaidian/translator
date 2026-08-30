from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TranslationHistoryEntry:
    id: int
    source_text: str
    translated_text: str
    source_language: str
    target_language: str
    provider: str
    model: str
    created_at: str
