"""Пакет для фильтрации электронных таблиц."""

from .filter_engine import FilterEngine
from .models import FilterCondition

__all__ = ["FilterCondition", "FilterEngine"]
