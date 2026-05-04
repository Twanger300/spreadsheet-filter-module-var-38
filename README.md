# Модуль фильтрации электронных таблиц

Учебный модуль для работы с электронными таблицами и фильтрами данных.
Поддерживаются CSV- и XLSX-файлы, фильтрация по одному или нескольким условиям,
сортировка и экспорт результата.

## Основные функции

- загрузка табличных данных из CSV/XLSX;
- фильтрация по условиям `equals`, `contains`, `gt`, `gte`, `lt`, `lte`, `between`, `in`, `not_empty`;
- объединение условий по логике `AND`/`OR`;
- сортировка строк по выбранному столбцу;
- сохранение фильтров в SQLite как пользовательских шаблонов;
- экспорт результата в CSV/XLSX.


## Быстрый запуск

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
pytest
```

Пример фильтрации CSV:

```bash
sheet-filter data/sample_sales.csv out.csv \
  --filter region equals Москва \
  --filter amount gte 50000 \
  --filter status equals Оплачено \
  --sort amount --desc
```

## Структура проекта

```text
src/spreadsheet_filter/
  cli.py            # запуск из командной строки
  filter_engine.py  # ядро фильтрации и сортировки
  io_helpers.py    # чтение и запись CSV/XLSX
  models.py         # модели условий фильтрации
  presets_db.py     # SQLite-хранилище шаблонов и журнала операций
```


## Запуск в PyCharm

1. Откройте папку `spreadsheet_filter_module` как проект.
2. В настройках проекта выберите интерпретатор Python 3.11 или новее. Код также совместим с Python 3.9, но для учебного отчета рекомендуется использовать Python 3.11.
3. Нажмите правой кнопкой на папку `src` и выберите `Mark Directory as` → `Sources Root`. Это убирает предупреждения IDE о неразрешенных импортах пакета.
4. Для запуска напрямую можно использовать файл `run_cli.py` в корне проекта.

Пример параметров запуска для `run_cli.py` или `cli.py`:

```text
data/sample_sales.csv data/result.csv --filter amount gte 50000 --sort amount --desc
```
