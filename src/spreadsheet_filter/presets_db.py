"""SQLite-хранилище шаблонов фильтрации и истории операций."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA = """
CREATE TABLE IF NOT EXISTS filter_presets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    conditions_json TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS operation_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    input_file TEXT NOT NULL,
    output_file TEXT NOT NULL,
    rows_before INTEGER NOT NULL,
    rows_after INTEGER NOT NULL,
    created_at TEXT NOT NULL
);
"""


class PresetRepository:
    """Репозиторий для сохранения шаблонов фильтрации и ведения журнала операций."""

    def __init__(self, db_path: str | Path = "filter_presets.db") -> None:
        self.db_path = db_path
        self._ensure_schema()

    def save_preset(self, name: str, conditions: list[dict[str, Any]]) -> None:
        """Сохраняет или обновляет шаблон фильтрации."""
        with sqlite3.connect(self.db_path) as connection:
            connection.execute(
                """
                INSERT INTO filter_presets(name, conditions_json, created_at)
                VALUES (?, ?, ?)
                ON CONFLICT(name) DO UPDATE SET
                    conditions_json = excluded.conditions_json,
                    created_at = excluded.created_at
                """,
                (name, json.dumps(conditions, ensure_ascii=False), self._now()),
            )

    def list_presets(self) -> list[dict[str, Any]]:
        """Возвращает список сохраненных шаблонов фильтрации."""
        with sqlite3.connect(self.db_path) as connection:
            rows = connection.execute(
                "SELECT id, name, conditions_json, created_at FROM filter_presets ORDER BY name"
            ).fetchall()
        return [
            {"id": row[0], "name": row[1], "conditions": json.loads(row[2]), "created_at": row[3]}
            for row in rows
        ]

    def log_operation(
        self,
        input_file: str,
        output_file: str,
        rows_before: int,
        rows_after: int,
    ) -> None:
        """Добавляет запись о выполненной фильтрации в журнал операций."""
        with sqlite3.connect(self.db_path) as connection:
            connection.execute(
                """
                INSERT INTO operation_log(input_file, output_file, rows_before, rows_after, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (input_file, output_file, rows_before, rows_after, self._now()),
            )

    def _ensure_schema(self) -> None:
        """Создает таблицы SQLite, если они еще не существуют."""
        with sqlite3.connect(self.db_path) as connection:
            connection.executescript(SCHEMA)

    @staticmethod
    def _now() -> str:
        """Возвращает текущую дату и время в формате ISO."""
        return datetime.now(tz=timezone.utc).isoformat()
