"""Логика фильтрации и сортировки строк таблицы."""

from __future__ import annotations

from collections.abc import Iterable
from decimal import Decimal, InvalidOperation
from typing import Any

from .models import FilterCondition

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
        if condition.operation not in self.SUPPORTED_OPERATIONS:
            raise ValueError(f"Неподдерживаемая операция фильтрации: {condition.operation}")

        value = row.get(condition.column)
        expected = condition.value

        match condition.operation:
            case "equals":
                return str(value).strip().lower() == str(expected).strip().lower()
            case "contains":
                return str(expected).strip().lower() in str(value).strip().lower()
            case "gt":
                return self._to_decimal(value) > self._to_decimal(expected)
            case "gte":
                return self._to_decimal(value) >= self._to_decimal(expected)
            case "lt":
                return self._to_decimal(value) < self._to_decimal(expected)
            case "lte":
                return self._to_decimal(value) <= self._to_decimal(expected)
            case "between":
                start, end = self._parse_range(expected)
                current = self._to_decimal(value)
                return start <= current <= end
            case "in":
                allowed = {str(item).strip().lower() for item in expected}
                return str(value).strip().lower() in allowed
            case "not_empty":
                return value is not None and str(value).strip() != ""
            case _:
                return False

    def _parse_range(self, value: Any) -> tuple[Decimal, Decimal]:
        if isinstance(value, str) and ".." in value:
            start, end = value.split("..", 1)
        elif isinstance(value, (tuple, list)) and len(value) == 2:
            start, end = value
        else:
            raise ValueError("Операция between ожидает значение формата 'начало..конец' или пару значений")
        return self._to_decimal(start), self._to_decimal(end)

    def _to_decimal(self, value: Any) -> Decimal:
        try:
            return Decimal(str(value).replace(",", ".").strip())
        except (InvalidOperation, AttributeError) as exc:
            raise ValueError(f"Невозможно сравнить нечисловое значение: {value!r}") from exc

    def _normalize_sort_value(self, value: Any) -> tuple[int, Any]:
        if value is None or str(value).strip() == "":
            return (1, "")
        try:
            return (0, self._to_decimal(value))
        except ValueError:
            return (0, str(value).strip().lower())
