"""Интерфейс командной строки для фильтрации электронных таблиц."""

from __future__ import annotations

import argparse
from pathlib import Path

from .filter_engine import FilterEngine
from .io import read_csv, read_xlsx, write_csv, write_xlsx
from .models import FilterCondition
from .presets_db import PresetRepository


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Filter CSV/XLSX spreadsheet data")
    parser.add_argument("input_file")
    parser.add_argument("output_file")
    parser.add_argument(
        "--filter",
        nargs=3,
        action="append",
        metavar=("COLUMN", "OPERATION", "VALUE"),
        default=[],
        help="Filter condition, for example: --filter amount gte 50000",
    )
    parser.add_argument("--logic", choices=["AND", "OR"], default="AND")
    parser.add_argument("--sort")
    parser.add_argument("--desc", action="store_true")
    parser.add_argument("--db", default="filter_presets.db")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_path = Path(args.input_file)
    output_path = Path(args.output_file)

    rows = read_xlsx(input_path) if input_path.suffix.lower() == ".xlsx" else read_csv(input_path)
    conditions = [FilterCondition(column, operation, value) for column, operation, value in args.filter]

    engine = FilterEngine()
    filtered_rows = engine.apply(rows, conditions, args.logic)
    if args.sort:
        filtered_rows = engine.sort(filtered_rows, args.sort, args.desc)

    if output_path.suffix.lower() == ".xlsx":
        write_xlsx(output_path, filtered_rows)
    else:
        write_csv(output_path, filtered_rows)

    PresetRepository(args.db).log_operation(
        str(input_path), str(output_path), len(rows), len(filtered_rows)
    )


if __name__ == "__main__":
    main()
