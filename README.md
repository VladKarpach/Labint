# Задача 11: Управление задачами (TODO)

**Студент:** Карпач В.Р

## Что сделано

Написаны юнит-тесты на `pytest` для модуля `main.py` (функции `create\_task`, `close\_task`, `open\_tasks`, `filter\_by\_priority`, `count\_closed`). Сам `main.py` не менялся.

## Файлы

* `main.py` — выданный модуль
* `test\_main.py` — тесты
* `requirements.txt` — зависимости (`pytest`, `pytest-cov`)
* `README.md` — этот файл

## Установка

```bash
pip install -r requirements.txt
```

## Запуск тестов

```bash
pytest -v
```

## Покрытие

```bash
pytest --cov=main --cov-report=term-missing
```

## Что проверяется

* `create\_task` — создание задачи (статус `open`), приоритеты 1 и 3, неверный приоритет (0 и 4) -> `ValueError`, повторный `id` -> `ValueError`
* `close\_task` — задача закрывается, повторное закрытие, несуществующий `id` -> `KeyError`
* `open\_tasks` — пустой словарь, сортировка, закрытые задачи не попадают в список
* `filter\_by\_priority` — выбор по приоритету с сортировкой, нет совпадений, пустой словарь
* `count\_closed` — пустой словарь, подсчёт закрытых задач

## Результат

Всего тестов: 16. Покрытие `main.py`: 100 %.

