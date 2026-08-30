"""本地翻译历史。"""

from history.models import TranslationHistoryEntry
from history.repository import HistoryRepository

__all__ = ["HistoryRepository", "TranslationHistoryEntry"]
