"""Тесты логики API на fake-Redis (реальный Redis для них не нужен)."""
import json
import sys
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "app"))

import server  # noqa: E402


class FakeRedis:
    """Минимальная имитация нужных команд sorted set."""

    def __init__(self):
        self.data = {}

    def ping(self):
        return True

    def zincrby(self, key, amount, member):
        self.data[member] = self.data.get(member, 0) + amount

    def zscore(self, key, member):
        return self.data.get(member)

    def _order(self):
        # как у Redis ZREVRANGE: очки по убыванию, при равенстве — ник по убыванию
        return sorted(self.data.items(), key=lambda kv: (kv[1], kv[0]), reverse=True)

    def zrevrank(self, key, member):
        names = [m for m, _ in self._order()]
        return names.index(member) if member in names else None

    def zrevrange(self, key, start, stop, withscores=False):
        return [(m, float(s)) for m, s in self._order()[start : stop + 1]]


class BrokenRedis(FakeRedis):
    def ping(self):
        raise ConnectionError("redis down")


def start(store):
    httpd = server.make_server(store, "secret", host="127.0.0.1", port=0)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd, f"http://127.0.0.1:{httpd.server_address[1]}"


def call(base, method, path, body=None, headers=None):
    req = urllib.request.Request(
        base + path,
        method=method,
        data=json.dumps(body).encode() if body is not None else None,
        headers={"Content-Type": "application/json", **(headers or {})},
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as err:
        return err.code, json.loads(err.read())


KEY = {"X-API-Key": "secret"}


class LeaderboardApiTest(unittest.TestCase):
    def setUp(self):
        self.httpd, self.base = start(FakeRedis())

    def tearDown(self):
        self.httpd.shutdown()
        self.httpd.server_close()

    def test_health_ok(self):
        self.assertEqual(call(self.base, "GET", "/health"), (200, {"status": "ok", "redis": "ok"}))

    def test_add_score_requires_key(self):
        status, _ = call(self.base, "POST", "/scores", {"nickname": "neo", "points": 5})
        self.assertEqual(status, 401)

    def test_add_score_accumulates(self):
        call(self.base, "POST", "/scores", {"nickname": "Neo", "points": 100}, KEY)
        status, data = call(self.base, "POST", "/scores", {"nickname": "neo", "points": 50}, KEY)
        self.assertEqual(status, 200)
        self.assertEqual(data, {"nickname": "neo", "score": 150, "rank": 1})

    def test_top_k_sorted_and_limited(self):
        for nick, pts in [("alice", 300), ("bobby", 500), ("carol", 100)]:
            call(self.base, "POST", "/scores", {"nickname": nick, "points": pts}, KEY)
        _, data = call(self.base, "GET", "/leaderboard?k=2")
        self.assertEqual([e["nickname"] for e in data["entries"]], ["bobby", "alice"])
        self.assertEqual([e["rank"] for e in data["entries"]], [1, 2])

    def test_k_larger_than_players(self):
        call(self.base, "POST", "/scores", {"nickname": "alice", "points": 10}, KEY)
        _, data = call(self.base, "GET", "/leaderboard?k=50")
        self.assertEqual(len(data["entries"]), 1)

    def test_tie_is_deterministic(self):
        call(self.base, "POST", "/scores", {"nickname": "alice", "points": 10}, KEY)
        call(self.base, "POST", "/scores", {"nickname": "bobby", "points": 10}, KEY)
        _, data = call(self.base, "GET", "/leaderboard")
        self.assertEqual([e["nickname"] for e in data["entries"]], ["bobby", "alice"])

    def test_player_rank(self):
        call(self.base, "POST", "/scores", {"nickname": "alice", "points": 10}, KEY)
        call(self.base, "POST", "/scores", {"nickname": "bobby", "points": 20}, KEY)
        _, data = call(self.base, "GET", "/players/ALICE")
        self.assertEqual(data, {"nickname": "alice", "score": 10, "rank": 2})

    def test_unknown_player_404(self):
        self.assertEqual(call(self.base, "GET", "/players/nobody")[0], 404)

    def test_validation_errors(self):
        bad = [
            {"nickname": "ab", "points": 5},
            {"nickname": "alice", "points": 0},
            {"nickname": "alice", "points": 10001},
            {"nickname": "alice", "points": "5"},
            {"nickname": "alice", "points": True},
        ]
        for body in bad:
            self.assertEqual(call(self.base, "POST", "/scores", body, KEY)[0], 400, body)
        self.assertEqual(call(self.base, "GET", "/leaderboard?k=0")[0], 400)
        self.assertEqual(call(self.base, "GET", "/leaderboard?k=101")[0], 400)


class HealthWithoutRedisTest(unittest.TestCase):
    def test_health_503_when_redis_down(self):
        httpd, base = start(BrokenRedis())
        try:
            status, data = call(base, "GET", "/health")
            self.assertEqual(status, 503)
            self.assertEqual(data["status"], "error")
        finally:
            httpd.shutdown()
            httpd.server_close()


if __name__ == "__main__":
    unittest.main()
