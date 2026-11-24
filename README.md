# Задача 11: Игровой рейтинг (лидерборд)

**Студент:** <Фамилия И.О.>

## Постановка

API рейтинга + Redis (sorted set или простой ключ-значение). Compose: `api` и `redis`. Обновить очки, топ-K. Dockerfile multi-stage (по возможности).

## Что реализовано

HTTP API лидерборда на Python (без веб-фреймворка, зависимость одна — клиент `redis`). Очки игроков хранятся в **Redis sorted set** `leaderboard`: член множества — ник, score — сумма очков. Топ-K и место игрока считаются самим Redis (`ZREVRANGE`, `ZREVRANK`).

| Метод и путь | Назначение |
|--------------|-----------|
| `POST /scores` | обновить очки: прибавить `points` игроку `nickname` (нужен заголовок `X-API-Key`) |
| `GET /leaderboard?k=10` | топ-K игроков, `k` от 1 до 100 |
| `GET /players/{nickname}` | очки и место игрока |
| `GET /health` | проверка API и связи с Redis |

Правила: ник — 3–20 символов `[A-Za-z0-9_-]`, регистр не важен (хранится в нижнем регистре); за одну операцию начисляется 1–10 000 очков; очки только прибавляются. При равенстве очков порядок определяет Redis: по нику в обратном алфавитном порядке.

## Структура

```
Dockerfile          # multi-stage сборка образа API
compose.yaml        # сервисы api и redis
.env.example        # пример переменных окружения
app/server.py       # приложение
app/requirements.txt
tests/test_app.py   # тесты логики (без Docker и Redis)
```

## Схема сервисов

| Сервис | Образ | Порт наружу | Том | Назначение |
|--------|-------|-------------|-----|-----------|
| `api` | собирается из `Dockerfile` | `8000` (меняется через `API_PORT`) | нет | HTTP API |
| `redis` | `redis:7-alpine` | **нет** (только внутри сети) | `redis-data:/data` | хранение очков, AOF-персистентность |

Оба сервиса в сети `leaderboard-net`. `api` обращается к Redis по имени сервиса `redis:6379`.

### Как устроен Dockerfile

1. **builder**: на образе `python:3.12-slim` устанавливает зависимости из `requirements.txt` в отдельный каталог `/install`.
2. **runtime**: чистый `python:3.12-slim`, в него копируются только установленные пакеты и код приложения. Запуск от непривилегированного пользователя `appuser`, в образе есть `HEALTHCHECK` по `/health`.

### Порядок старта

`redis` имеет healthcheck (`redis-cli ping`). У `api` стоит `depends_on: redis: condition: service_healthy`, поэтому API запускается только когда Redis уже отвечает.

## Запуск

Нужен Docker с Compose v2.

```bash
cp .env.example .env        # PowerShell: Copy-Item .env.example .env
docker compose up --build
```

В `.env` задайте свой `LEADERBOARD_API_KEY`. Файл `.env` в репозиторий не попадает; в коде реальных секретов нет.

## Проверка

Статус контейнеров (оба должны быть `healthy`):

```bash
docker compose ps
```

Проверка API (примеры для bash; в PowerShell используйте `curl.exe` и экранируйте кавычки так, как показано ниже):

```bash
# здоровье
curl http://localhost:8000/health

# начислить очки
curl -X POST http://localhost:8000/scores \
  -H "Content-Type: application/json" -H "X-API-Key: change-me" \
  -d '{"nickname":"neo","points":250}'
curl -X POST http://localhost:8000/scores \
  -H "Content-Type: application/json" -H "X-API-Key: change-me" \
  -d '{"nickname":"trinity","points":400}'

# топ-2
curl "http://localhost:8000/leaderboard?k=2"

# игрок
curl http://localhost:8000/players/neo
```

PowerShell:

```powershell
curl.exe http://localhost:8000/health
curl.exe -X POST http://localhost:8000/scores -H "Content-Type: application/json" -H "X-API-Key: change-me" -d "{\"nickname\":\"neo\",\"points\":250}"
curl.exe "http://localhost:8000/leaderboard?k=2"
```

Ожидаемо: после начислений в топе `trinity` (400) на 1 месте, `neo` (250) на 2-м. Запрос без ключа возвращает `401`.

Данные переживают перезапуск: `docker compose restart` или `docker compose down` и снова `up` (том `redis-data` сохраняется). Полностью очистить: `docker compose down -v`.

Логи приложения: `docker compose logs -f api`.

## Тесты

Тесты проверяют логику API на имитации Redis, поэтому запускаются без Docker:

```bash
python -m unittest discover -s tests -v
```

## Остановка

```bash
docker compose down        # остановить, данные сохранить
docker compose down -v     # остановить и удалить том с данными
```
