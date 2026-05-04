\# Генерация API-документации



Для генерации HTML-документации используется стандартный модуль pydoc.



Команды запуска из корня проекта:



python -m pip install -e .\[dev]

New-Item -ItemType Directory -Force -Path "docs\\api"

Push-Location "docs\\api"

python -m pydoc -w spreadsheet\_filter.filter\_engine

python -m pydoc -w spreadsheet\_filter.models

python -m pydoc -w spreadsheet\_filter.io\_helpers

python -m pydoc -w spreadsheet\_filter.presets\_db

Pop-Location



Сгенерированные HTML-файлы размещаются в каталоге docs/api.



Документация используется для просмотра модулей, классов, методов и docstring разработанного проекта.

