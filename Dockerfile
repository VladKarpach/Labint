# syntax=docker/dockerfile:1

# ---- Этап 1: сборка зависимостей ----
FROM python:3.12-slim AS builder
WORKDIR /build
COPY app/requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ---- Этап 2: минимальный рантайм-образ ----
FROM python:3.12-slim AS runtime
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# запуск не от root
RUN useradd --create-home --uid 10001 appuser

WORKDIR /srv/app
COPY --from=builder /install /usr/local
COPY app/ .
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2)"

CMD ["python", "server.py"]
