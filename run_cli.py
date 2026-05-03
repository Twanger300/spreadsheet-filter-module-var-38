"""Упрощенный запуск CLI из корня проекта, в том числе через PyCharm."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
SRC_DIR = PROJECT_ROOT / "src"

# Добавляем папку src в путь импорта, чтобы Python видел пакет spreadsheet_filter.
sys.path.insert(0, str(SRC_DIR))

from spreadsheet_filter.cli import main


if __name__ == "__main__":
    main()
