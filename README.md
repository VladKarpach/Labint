# Задача 11: Управление задачами (TODO)

**Студент:** Фамилия И.О.

## Что сделано

Написаны юнит-тесты на `pytest` для модуля `main.py` (функции `create_task`, `close_task`, `open_tasks`, `filter_by_priority`, `count_closed`). Сам `main.py` не менялся.

## Файлы

- `main.py` — выданный модуль
- `test_main.py` — тесты
- `requirements.txt` — зависимости (`pytest`, `pytest-cov`)
- `README.md` — этот файл

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

- `create_task` — создание задачи (статус `open`), приоритеты 1 и 3, неверный приоритет (0 и 4) -> `ValueError`, повторный `id` -> `ValueError`
- `close_task` — задача закрывается, повторное закрытие, несуществующий `id` -> `KeyError`
- `open_tasks` — пустой словарь, сортировка, закрытые задачи не попадают в список
- `filter_by_priority` — выбор по приоритету с сортировкой, нет совпадений, пустой словарь
- `count_closed` — пустой словарь, подсчёт закрытых задач

## Результат

Всего тестов: 16. Покрытие `main.py`: 100 %.
