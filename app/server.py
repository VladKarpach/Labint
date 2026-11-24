"""API игрового рейтинга (лидерборда) на Redis sorted set.

Очки игроков лежат в одном sorted set с ключом `leaderboard`:
член множества — ник (в нижнем регистре), score — сумма очков.
"""
import json
import os
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

LEADERBOARD_KEY = "leaderboard"
NICK_RE = re.compile(r"^[A-Za-z0-9_-]{3,20}$")
MAX_POINTS = 10000
MAX_K = 100


def connect():
    """Создаёт клиент Redis по переменным окружения."""
    import redis  # импорт здесь, чтобы тесты могли подставить fake-хранилище

    return redis.Redis(
        host=os.environ.get("REDIS_HOST", "redis"),
        port=int(os.environ.get("REDIS_PORT", "6379")),
        decode_responses=True,
    )


def add_score(store, nickname, points):
    """Прибавляет очки игроку и возвращает его актуальные данные."""
    store.zincrby(LEADERBOARD_KEY, points, nickname)
    return get_player(store, nickname)


def get_player(store, nickname):
    score = store.zscore(LEADERBOARD_KEY, nickname)
    if score is None:
        return None
    rank = store.zrevrank(LEADERBOARD_KEY, nickname)
    return {"nickname": nickname, "score": int(score), "rank": rank + 1}


def get_top(store, k):
    rows = store.zrevrange(LEADERBOARD_KEY, 0, k - 1, withscores=True)
    return [
        {"rank": i, "nickname": member, "score": int(score)}
        for i, (member, score) in enumerate(rows, start=1)
    ]


def make_server(store, api_key, host="0.0.0.0", port=8000):
    class Handler(BaseHTTPRequestHandler):
        def _send(self, status, body):
            data = json.dumps(body, ensure_ascii=False).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def _error(self, status, message):
            self._send(status, {"error": message})

        def log_message(self, fmt, *args):
            # логи идут в stdout контейнера: docker compose logs api
            print(f"{self.address_string()} {fmt % args}", flush=True)

        def do_GET(self):
            url = urlparse(self.path)
            if url.path == "/health":
                try:
                    store.ping()
                except Exception:
                    return self._send(503, {"status": "error", "redis": "unavailable"})
                return self._send(200, {"status": "ok", "redis": "ok"})

            if url.path == "/leaderboard":
                raw = parse_qs(url.query).get("k", ["10"])[0]
                if not raw.isdigit() or not 1 <= int(raw) <= MAX_K:
                    return self._error(400, f"k must be an integer from 1 to {MAX_K}")
                return self._send(200, {"entries": get_top(store, int(raw))})

            match = re.fullmatch(r"/players/([^/]+)", url.path)
            if match:
                nick = match.group(1)
                if not NICK_RE.match(nick):
                    return self._error(400, "invalid nickname")
                player = get_player(store, nick.lower())
                if player is None:
                    return self._error(404, "player not found")
                return self._send(200, player)

            self._error(404, "not found")

        def do_POST(self):
            if urlparse(self.path).path != "/scores":
                return self._error(404, "not found")
            if self.headers.get("X-API-Key") != api_key:
                return self._error(401, "invalid or missing API key")
            try:
                length = int(self.headers.get("Content-Length", 0))
                body = json.loads(self.rfile.read(length) or b"{}")
            except (ValueError, json.JSONDecodeError):
                return self._error(400, "body must be valid JSON")
            if not isinstance(body, dict):
                return self._error(400, "body must be a JSON object")
            nick, points = body.get("nickname"), body.get("points")
            if not isinstance(nick, str) or not NICK_RE.match(nick):
                return self._error(400, "invalid nickname")
            if isinstance(points, bool) or not isinstance(points, int) or not 1 <= points <= MAX_POINTS:
                return self._error(400, f"points must be an integer from 1 to {MAX_POINTS}")
            self._send(200, add_score(store, nick.lower(), points))

    return ThreadingHTTPServer((host, port), Handler)


def main():
    api_key = os.environ.get("LEADERBOARD_API_KEY", "change-me")
    server = make_server(connect(), api_key)
    print("Leaderboard API слушает порт 8000", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
