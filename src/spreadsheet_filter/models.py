"""Модели данных для фильтрации электронных таблиц."""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class FilterCondition:
    """Одно условие фильтрации, применяемое к столбцу таблицы."""

    column: str
    operation: str
    value: Any = None
