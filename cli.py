"""Интерфейс командной строки для фильтрации электронных таблиц."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    from .filter_engine import FilterEngine
    from .io import read_csv, read_xlsx, write_csv, write_xlsx
    from .models import FilterCondition
    from .presets_db import PresetRepository
except ImportError:  # Позволяет запускать cli.py напрямую из IDE, например из PyCharm
    package_root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(package_root))

    from spreadsheet_filter.filter_engine import FilterEngine
    from spreadsheet_filter.io import read_csv, read_xlsx, write_csv, write_xlsx
    from spreadsheet_filter.models import FilterCondition
    from spreadsheet_filter.presets_db import PresetRepository


class RussianArgumentParser(argparse.ArgumentParser):
    """ArgumentParser с русскими служебными сообщениями."""

    def format_usage(self) -> str:
        """Возвращает строку использования с русским заголовком."""
        return super().format_usage().replace("usage:", "использование:")

    def format_help(self) -> str:
        """Возвращает справку с русским заголовком строки использования."""
        return super().format_help().replace("usage:", "использование:")

    def error(self, message: str) -> None:
        """Выводит сообщение об ошибке на русском языке."""
        translated_message = self._translate_error(message)
        self.print_usage(sys.stderr)
        self.exit(2, f"{self.prog}: ошибка: {translated_message}\n")

    @staticmethod
    def _translate_error(message: str) -> str:
        """Переводит типовые сообщения argparse на русский язык."""
        replacements = {
            "the following arguments are required:": "обязательные аргументы не указаны:",
            "unrecognized arguments:": "неизвестные аргументы:",
            "expected 3 arguments": "ожидалось 3 значения",
            "invalid choice:": "недопустимое значение:",
            "choose from": "доступные значения",
        }
        for source, target in replacements.items():
            message = message.replace(source, target)
        return message


def parse_args() -> argparse.Namespace:
    """Разбирает аргументы командной строки."""
    parser = RussianArgumentParser(
        description="Фильтрация данных в CSV- и XLSX-таблицах",
        add_help=False,
    )
    parser._positionals.title = "обязательные аргументы"
    parser._optionals.title = "параметры"
    parser.add_argument(
        "-h",
        "--help",
        action="help",
        default=argparse.SUPPRESS,
        help="показать справку и завершить работу",
    )
    parser.add_argument("input_file", metavar="ВХОДНОЙ_ФАЙЛ", help="Путь к входному CSV- или XLSX-файлу")
    parser.add_argument("output_file", metavar="ФАЙЛ_РЕЗУЛЬТАТА", help="Путь к файлу результата")
    parser.add_argument(
        "--filter",
        nargs=3,
        action="append",
        metavar=("СТОЛБЕЦ", "ОПЕРАЦИЯ", "ЗНАЧЕНИЕ"),
        default=[],
        help=(
            "Условие фильтрации. Пример: --filter amount gte 50000. "
            "Операции: equals, contains, gt, gte, lt, lte, between, in, not_empty"
        ),
    )
    parser.add_argument(
        "--logic",
        choices=["AND", "OR"],
        default="AND",
        help="Логика объединения условий: AND — все условия, OR — хотя бы одно условие",
    )
    parser.add_argument("--sort", metavar="СТОЛБЕЦ", help="Столбец для сортировки результата")
    parser.add_argument("--desc", action="store_true", help="Сортировать по убыванию")
    parser.add_argument("--db", metavar="БД", default="filter_presets.db", help="Путь к SQLite-базе журнала операций")
    return parser.parse_args()


def main() -> None:
    """Выполняет загрузку таблицы, фильтрацию, сортировку и сохранение результата."""
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

    print(
        "Фильтрация завершена. "
        f"Строк до обработки: {len(rows)}. "
        f"Строк после обработки: {len(filtered_rows)}. "
        f"Файл результата: {output_path}"
    )


if __name__ == "__main__":
    main()
