import sqlite3
from pathlib import Path

from spreadsheet_filter.presets_db import PresetRepository

db_path = Path("data/filter_presets.db")

if db_path.exists():
    db_path.unlink()

repo = PresetRepository(db_path)

repo.save_preset(
    "Продажи от 50000",
    [
        {
            "column": "amount",
            "operation": "gte",
            "value": "50000",
        }
    ],
)

repo.log_operation(
    input_file="data/sample_sales.csv",
    output_file="data/result.csv",
    rows_before=6,
    rows_after=4,
)

print("SQLite-база создана:", db_path)
print()

print("Список шаблонов фильтрации:")
for preset in repo.list_presets():
    print(preset)

print()
print("Таблицы базы данных:")
with sqlite3.connect(db_path) as connection:
    tables = connection.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    ).fetchall()
    for table in tables:
        print(table[0])

    print()
    print("Содержимое таблицы filter_presets:")
    for row in connection.execute(
        "SELECT id, name, conditions_json, created_at FROM filter_presets"
    ):
        print(row)

    print()
    print("Содержимое таблицы operation_log:")
    for row in connection.execute(
        "SELECT id, input_file, output_file, rows_before, rows_after, created_at FROM operation_log"
    ):
        print(row)
