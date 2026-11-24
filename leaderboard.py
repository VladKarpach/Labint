"""Лидерборд игроков: обновление очков и топ-K.

Правила
-------
* Очки только прибавляются: ``add_score`` принимает целое число > 0.
* Ник нормализуется (NFKC, обрезка пробелов, без учёта регистра):
  «Neo» и « neo » — один игрок. В таблице показывается первое написание.
* Порядок: больше очков — выше. При равенстве выше тот, кто набрал
  текущее количество очков раньше (порядок определяется счётчиком
  обновлений, а не часами, поэтому поведение детерминировано и тестируется).
* Места уникальны: 1, 2, 3, ... (без одинаковых мест при ничьей).

Сложность: ``add_score`` — O(1); ``top(k)`` — O(n log k); ``rank_of`` — O(n).
"""
import heapq
import unicodedata
from dataclasses import dataclass
from threading import RLock


@dataclass(frozen=True)
class Entry:
    rank: int
    player: str
    score: int


def _normalize(nickname):
    if not isinstance(nickname, str):
        raise TypeError("ник должен быть строкой")
    cleaned = unicodedata.normalize("NFKC", nickname).strip()
    if not cleaned:
        raise ValueError("ник не может быть пустым")
    return cleaned


class Leaderboard:
    def __init__(self):
        self._lock = RLock()
        self._scores = {}    # ключ ника -> очки
        self._names = {}     # ключ ника -> отображаемое имя (первое написание)
        self._reached = {}   # ключ ника -> номер обновления, когда набраны текущие очки
        self._counter = 0

    def add_score(self, nickname, points):
        """Прибавляет очки игроку (создаёт игрока при первом начислении)."""
        if isinstance(points, bool) or not isinstance(points, int):
            raise TypeError("очки должны быть целым числом")
        if points <= 0:
            raise ValueError("очки должны быть положительными")
        display = _normalize(nickname)
        key = display.casefold()
        with self._lock:
            self._counter += 1
            self._names.setdefault(key, display)
            self._scores[key] = self._scores.get(key, 0) + points
            self._reached[key] = self._counter
            return self._scores[key]

    def _sort_key(self, key):
        return (-self._scores[key], self._reached[key])

    def top(self, k):
        """Топ-K игроков. K больше числа игроков — вернёт всех; K = 0 — пустой список."""
        if isinstance(k, bool) or not isinstance(k, int):
            raise TypeError("k должно быть целым числом")
        if k < 0:
            raise ValueError("k не может быть отрицательным")
        with self._lock:
            best = heapq.nsmallest(k, self._scores, key=self._sort_key)
            return [
                Entry(rank, self._names[key], self._scores[key])
                for rank, key in enumerate(best, start=1)
            ]

    def rank_of(self, nickname):
        """Место игрока (1 — лидер) или None, если игрока нет в таблице."""
        key = _normalize(nickname).casefold()
        with self._lock:
            if key not in self._scores:
                return None
            mine = self._sort_key(key)
            return 1 + sum(1 for other in self._scores if self._sort_key(other) < mine)

    def reset(self):
        """Очищает таблицу (например, при смене сезона)."""
        with self._lock:
            self._scores.clear()
            self._names.clear()
            self._reached.clear()
            self._counter = 0

    def __len__(self):
        with self._lock:
            return len(self._scores)
