"""Учебный stub API лидерборда (только стандартная библиотека, данные в памяти).

Запуск:  python src/server.py
Swagger UI:  http://localhost:8000/docs
"""
import json
import os
import re
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parent.parent
API_KEY = os.environ.get("LEADERBOARD_API_KEY", "dev-api-key")
ADMIN_TOKEN = os.environ.get("LEADERBOARD_ADMIN_TOKEN", "dev-admin-token")
PORT = int(os.environ.get("PORT", "8000"))

NICK_RE = re.compile(r"^[A-Za-z0-9_-]{3,20}$")
MAX_POINTS = 10000


def iso(ts):
    return datetime.fromtimestamp(ts, timezone.utc).isoformat().replace("+00:00", "Z")


class State:
    def __init__(self):
        self.season_id = 1
        self.season_started = time.time()
        self.players = {}   # ключ — ник в нижнем регистре
        self.archive = []   # завершённые сезоны

    def ranking(self):
        return sorted(
            self.players.values(),
            key=lambda p: (-p["score"], p["reached_at"], p["nickname"].lower()),
        )

    def player_view(self, key):
        ranked = self.ranking()
        for position, p in enumerate(ranked, start=1):
            if p["nickname"].lower() == key:
                return {
                    "nickname": p["nickname"],
                    "score": p["score"],
                    "rank": position,
                    "updated_at": iso(p["reached_at"]),
                }
        return None


STATE = State()

SWAGGER_PAGE = """<!doctype html>
<html lang="ru"><head><meta charset="utf-8"><title>Leaderboard API</title>
<link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css">
</head><body><div id="ui"></div>
<script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
<script>SwaggerUIBundle({url: "/openapi.yaml", dom_id: "#ui"});</script>
</body></html>"""


class Handler(BaseHTTPRequestHandler):
    def _send(self, status, body, content_type="application/json"):
        data = body if isinstance(body, bytes) else json.dumps(body, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", f"{content_type}; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _error(self, status, message):
        self._send(status, {"error": message})

    def _json_body(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            payload = json.loads(self.rfile.read(length) or b"{}")
            return payload if isinstance(payload, dict) else None
        except (ValueError, json.JSONDecodeError):
            return None

    def log_message(self, fmt, *args):
        pass

    def do_GET(self):
        url = urlparse(self.path)
        path = url.path

        if path == "/health":
            return self._send(200, {"status": "ok"})
        if path == "/docs":
            return self._send(200, SWAGGER_PAGE.encode(), "text/html")
        if path == "/openapi.yaml":
            return self._send(200, (ROOT / "openapi.yaml").read_bytes(), "application/yaml")
        if path == "/season":
            return self._send(200, {
                "id": STATE.season_id,
                "started_at": iso(STATE.season_started),
                "players_count": len(STATE.players),
            })
        if path == "/leaderboard":
            raw = parse_qs(url.query).get("k", ["10"])[0]
            if not raw.isdigit() or not 1 <= int(raw) <= 100:
                return self._error(400, "k must be an integer from 1 to 100")
            entries = [
                {"rank": i, "nickname": p["nickname"], "score": p["score"]}
                for i, p in enumerate(STATE.ranking()[: int(raw)], start=1)
            ]
            return self._send(200, {"season": STATE.season_id, "entries": entries})
        match = re.fullmatch(r"/players/([^/]+)", path)
        if match:
            nick = match.group(1)
            if not NICK_RE.match(nick):
                return self._error(400, "invalid nickname")
            view = STATE.player_view(nick.lower())
            if view is None:
                return self._error(404, "player not found")
            return self._send(200, view)
        self._error(404, "not found")

    def do_POST(self):
        path = urlparse(self.path).path

        if path == "/scores":
            if self.headers.get("X-API-Key") != API_KEY:
                return self._error(401, "invalid or missing API key")
            body = self._json_body()
            if body is None:
                return self._error(400, "body must be a JSON object")
            nick, points = body.get("nickname"), body.get("points")
            if not isinstance(nick, str) or not NICK_RE.match(nick):
                return self._error(400, "invalid nickname")
            if isinstance(points, bool) or not isinstance(points, int) or not 1 <= points <= MAX_POINTS:
                return self._error(400, f"points must be an integer from 1 to {MAX_POINTS}")
            key = nick.lower()
            player = STATE.players.setdefault(
                key, {"nickname": nick, "score": 0, "reached_at": time.time()}
            )
            player["score"] += points
            player["reached_at"] = time.time()
            return self._send(200, STATE.player_view(key))

        if path == "/season/reset":
            if self.headers.get("X-Admin-Token") != ADMIN_TOKEN:
                return self._error(401, "invalid or missing admin token")
            body = self._json_body()
            if body is None or body.get("confirm") is not True:
                return self._error(400, "confirm must be true")
            archived = len(STATE.players)
            STATE.archive.append({
                "season": STATE.season_id,
                "results": [
                    {"nickname": p["nickname"], "score": p["score"]} for p in STATE.ranking()
                ],
            })
            previous = STATE.season_id
            STATE.season_id += 1
            STATE.season_started = time.time()
            STATE.players = {}
            return self._send(200, {
                "previous_season": previous,
                "new_season": STATE.season_id,
                "archived_players": archived,
            })

        self._error(404, "not found")


def main():
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    print(f"Leaderboard stub: http://localhost:{PORT}/docs")
    server.serve_forever()


if __name__ == "__main__":
    main()
