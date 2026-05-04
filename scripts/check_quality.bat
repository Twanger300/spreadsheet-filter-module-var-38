@echo off
python -m pip install -e .[dev]
pytest
ruff check src tests
python -m build
