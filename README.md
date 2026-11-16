# Задача 11: Конвертер температуры

**Студент:** Карпач В.Р.

## Постановка задачи

Реализуйте:

```python
# main.py
def c\_to\_f(c: float) -> float:
    ...

def f\_to\_c(f: float) -> float:
    ...

def c\_to\_k(c: float) -> float:
    """Ниже абсолютного нуля (−273.15 °C) — ValueError."""
    ...
```

BDD: точка замерзания/кипения воды, ошибка ниже абсолютного нуля.

Требования: юнит-тесты на `pytest` (не менее 5), BDD-сценарии Gherkin с рабочими шагами через `pytest-bdd` (не менее 3), описание цикла red → green → refactor.

## Структура репозитория

```
main.py                          реализация функций
pytest.ini                       настройки pytest (pythonpath, каталог тестов)
requirements.txt                 pytest, pytest-bdd, pytest-cov
tests/test\_main.py               юнит-тесты
tests/test\_bdd\_temperature.py    step definitions для BDD
features/temperature.feature     сценарии Gherkin (английский язык)
```

## Установка

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
```

## Запуск юнит-тестов

```bash
pytest tests/test\_main.py -v
```

## Запуск BDD

```bash
pytest tests/test\_bdd\_temperature.py -v
```

Все тесты сразу, с покрытием:

```bash
pytest --cov=main --cov-report=term-missing
```

## Что проверяется

### Юнит-тесты (26 проверок с учётом параметризации)

|Функция|Сценарии|
|-|-|
|`c\_to\_f`|0 °C → 32 °F, 100 °C → 212 °F, −40 °C → −40 °F, 37 °C → 98.6 °F, абсолютный ноль → −459.67 °F, дробные значения|
|`f\_to\_c`|те же опорные точки в обратную сторону|
|`c\_to\_f` + `f\_to\_c`|взаимная обратность на наборе значений (−100 … 1000 °C)|
|`c\_to\_k`|0 °C → 273.15 K, 100 °C → 373.15 K, отрицательные и дробные значения|
|`c\_to\_k` (граница)|−273.15 °C допустим и даёт 0 K|
|`c\_to\_k` (ошибки)|−273.16, −274, −300, −1000 → `ValueError("temperature below absolute zero")`|

Сравнение чисел с плавающей точкой выполняется через `pytest.approx`, а не через `==`.

### BDD-сценарии (`features/temperature.feature`)

|Сценарий|Что описывает|
|-|-|
|Freezing and boiling point of water from Celsius (Outline: 0, 100, −40)|Цельсий → Фаренгейт|
|Fahrenheit to Celsius (Outline: 32, 212)|Фаренгейт → Цельсий|
|Celsius to Kelvin for water points (Outline: 0, 100)|Цельсий → Кельвин|
|Absolute zero is the lowest allowed temperature|граница: −273.15 °C = 0 K|
|Temperature below absolute zero is rejected|−300 °C → ошибка|

Всего 9 прогонов сценариев (3 Scenario Outline с примерами + 2 обычных сценария). Шаги реально выполняются: `Given` сохраняет входное значение, `When` вызывает функцию из `main.py` (в «ошибочном» сценарии — внутри `try/except`), `Then` сравнивает результат или проверяет текст исключения.

## Red–Green–Refactor (кратко)

Работа велась по test-first: сначала тесты и сценарии, потом реализация. Удобно фиксировать каждый шаг отдельным коммитом (`red: ...`, `green: ...`, `refactor: ...`).

### Пример 1: `c\_to\_f`

**Red.** В `main.py` лежит заглушка `def c\_to\_f(c): ...` (возвращает `None`). Написан тест `test\_c\_to\_f\_known\_points` и сценарий «Freezing and boiling point of water from Celsius».

```
FAILED tests/test\_main.py::test\_c\_to\_f\_known\_points\[0-32]
    assert None == approx(32)
```

**Green.** Минимальная реализация, которая проходит тесты:

```python
def c\_to\_f(c: float) -> float:
    return c \* 9 / 5 + 32
```

После этого все проверки зелёные. Числа с плавающей точкой (например, 37 °C → 98.6 °F) сравниваются через `pytest.approx`, а не через `==`, поэтому тесты не зависят от ошибок округления.

**Refactor.** Формулы вынесены в понятные константы и добавлена параметризованная проверка обратимости `f\_to\_c(c\_to\_f(x)) == x`, которая ловит ошибки в одной из двух функций, если они разойдутся.

### Пример 2: `c\_to\_k` и граница абсолютного нуля

**Red.** Сначала написаны тест на ошибку и сценарий «Temperature below absolute zero is rejected». Заглушка ничего не бросает:

```
FAILED tests/test\_main.py::test\_c\_to\_k\_below\_absolute\_zero\_raises\[-300]
    Failed: DID NOT RAISE <class 'ValueError'>
```

**Green.** Добавлена проверка и перевод в кельвины:

```python
def c\_to\_k(c: float) -> float:
    if c < -273.15:
        raise ValueError("temperature below absolute zero")
    return c + 273.15
```

Отдельный тест `test\_c\_to\_k\_absolute\_zero\_is\_allowed...` фиксирует, что условие строгое (`<`, а не `<=`): сам абсолютный ноль допустим.

**Refactor.** Магические числа заменены именованными константами `ABSOLUTE\_ZERO\_C` и `KELVIN\_OFFSET`; тесты используют `ABSOLUTE\_ZERO\_C`, поэтому при смене константы граничный тест остаётся осмысленным. Итоговый код — в `main.py`.

## Итог

Юнит-тесты и BDD-сценарии проверяют одну и ту же реализацию `main.py`: юнит-тесты фиксируют точные числа и границы, сценарии Gherkin описывают то же поведение читаемым языком.

