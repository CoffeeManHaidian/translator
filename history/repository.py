import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from PySide6.QtCore import QStandardPaths

from history.models import TranslationHistoryEntry
from translation.models import TranslationRequest


class HistoryRepository:
    """通过 SQLite 保存成功完成的翻译。"""

    def __init__(self, database_path: str | Path | None = None) -> None:
        if database_path is None:
            data_directory = Path(
                QStandardPaths.writableLocation(
                    QStandardPaths.StandardLocation.AppDataLocation
                )
            )
            data_directory.mkdir(parents=True, exist_ok=True)
            database_path = data_directory / "translation_history.sqlite3"
        elif str(database_path) != ":memory:":
            Path(database_path).parent.mkdir(parents=True, exist_ok=True)

        self._connection = sqlite3.connect(str(database_path))
        self._connection.row_factory = sqlite3.Row
        self._create_schema()

    def _create_schema(self) -> None:
        self._connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS translation_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_text TEXT NOT NULL,
                translated_text TEXT NOT NULL,
                source_language TEXT NOT NULL,
                target_language TEXT NOT NULL,
                provider TEXT NOT NULL,
                model TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_translation_history_created_at
            ON translation_history(created_at DESC, id DESC);
            """
        )
        self._connection.commit()

    def add(
        self,
        request: TranslationRequest,
        translated_text: str,
        provider: str,
        model: str,
    ) -> int | None:
        translated_text = translated_text.strip()
        if not request.text.strip() or not translated_text:
            return None

        cursor = self._connection.execute(
            """
            INSERT INTO translation_history (
                source_text,
                translated_text,
                source_language,
                target_language,
                provider,
                model,
                created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                request.text.strip(),
                translated_text,
                request.source_language,
                request.target_language,
                provider.strip(),
                model.strip(),
                datetime.now(timezone.utc).isoformat(timespec="seconds"),
            ),
        )
        self._connection.commit()
        return int(cursor.lastrowid)

    def list_recent(self, limit: int = 100) -> list[TranslationHistoryEntry]:
        safe_limit = max(1, min(int(limit), 500))
        rows = self._connection.execute(
            """
            SELECT
                id,
                source_text,
                translated_text,
                source_language,
                target_language,
                provider,
                model,
                created_at
            FROM translation_history
            ORDER BY created_at DESC, id DESC
            LIMIT ?
            """,
            (safe_limit,),
        ).fetchall()
        return [TranslationHistoryEntry(**dict(row)) for row in rows]

    def clear(self) -> None:
        self._connection.execute("DELETE FROM translation_history")
        self._connection.commit()

    def close(self) -> None:
        self._connection.close()
