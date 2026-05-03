"""Логика фильтрации и сортировки строк таблицы."""

from __future__ import annotations

from collections.abc import Iterable
from decimal import Decimal, InvalidOperation
from typing import Any

try:
    from .models import FilterCondition
except ImportError:
    # Этот импорт используется при прямом запуске cli.py из папки spreadsheet_filter.
    from models import FilterCondition

Row = dict[str, Any]


class FilterEngine:
    """Применяет условия фильтрации к строкам, загруженным из электронной таблицы."""

    SUPPORTED_OPERATIONS = {
        "equals",
        "contains",
        "gt",
        "gte",
        "lt",
        "lte",
        "between",
        "in",
        "not_empty",
    }

    def apply(
        self,
        rows: Iterable[Row],
        conditions: Iterable[FilterCondition],
        logic: str = "AND",
    ) -> list[Row]:
        """Возвращает строки, которые соответствуют всем условиям или хотя бы одному условию."""
        normalized_logic = logic.upper()
        if normalized_logic not in {"AND", "OR"}:
            raise ValueError("Логика фильтрации должна быть AND или OR")

        conditions = list(conditions)
        if not conditions:
            return list(rows)

        result: list[Row] = []
        for row in rows:
            checks = [self._matches(row, condition) for condition in conditions]
            if (normalized_logic == "AND" and all(checks)) or (
                normalized_logic == "OR" and any(checks)
            ):
                result.append(row)
        return result

    def sort(self, rows: Iterable[Row], column: str, descending: bool = False) -> list[Row]:
        """Сортирует строки по выбранному столбцу."""
        return sorted(rows, key=lambda row: self._normalize_sort_value(row.get(column)), reverse=descending)

    def _matches(self, row: Row, condition: FilterCondition) -> bool:
        """Проверяет соответствие одной строки одному условию фильтрации."""
        if condition.operation not in self.SUPPORTED_OPERATIONS:
            raise ValueError(f"Неподдерживаемая операция фильтрации: {condition.operation}")

        value = row.get(condition.column)
        expected = condition.value
        operation = condition.operation

        if operation == "equals":
            return str(value).strip().lower() == str(expected).strip().lower()
        if operation == "contains":
            return str(expected).strip().lower() in str(value).strip().lower()
        if operation == "gt":
            return self._to_decimal(value) > self._to_decimal(expected)
        if operation == "gte":
            return self._to_decimal(value) >= self._to_decimal(expected)
        if operation == "lt":
            return self._to_decimal(value) < self._to_decimal(expected)
        if operation == "lte":
            return self._to_decimal(value) <= self._to_decimal(expected)
        if operation == "between":
            start, end = self._parse_range(expected)
            current = self._to_decimal(value)
            return start <= current <= end
        if operation == "in":
            allowed = {str(item).strip().lower() for item in str(expected).split(",")}
            return str(value).strip().lower() in allowed
        if operation == "not_empty":
            return value is not None and str(value).strip() != ""
        return False

    @staticmethod
    def _parse_range(value: Any) -> tuple[Decimal, Decimal]:
        """Преобразует диапазон фильтрации в пару числовых границ."""
        if isinstance(value, str) and ".." in value:
            start, end = value.split("..", 1)
        elif isinstance(value, (tuple, list)) and len(value) == 2:
            start, end = value
        else:
            raise ValueError("Операция between ожидает значение формата 'начало..конец' или пару значений")
        return FilterEngine._to_decimal(start), FilterEngine._to_decimal(end)

    @staticmethod
    def _to_decimal(value: Any) -> Decimal:
        """Преобразует значение в Decimal для корректного числового сравнения."""
        try:
            return Decimal(str(value).replace(",", ".").strip())
        except (InvalidOperation, AttributeError) as exc:
            raise ValueError(f"Невозможно сравнить нечисловое значение: {value!r}") from exc

    @staticmethod
    def _normalize_sort_value(value: Any) -> tuple[int, Any]:
        """Нормализует значение перед сортировкой."""
        if value is None or str(value).strip() == "":
            return 1, ""
        try:
            return 0, FilterEngine._to_decimal(value)
        except ValueError:
            return 0, str(value).strip().lower()
