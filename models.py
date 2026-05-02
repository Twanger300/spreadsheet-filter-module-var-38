"""Data models for spreadsheet filtering."""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class FilterCondition:
    """Single filter condition applied to a spreadsheet column."""

    column: str
    operation: str
    value: Any = None
