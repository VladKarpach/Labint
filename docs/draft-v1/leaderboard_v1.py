"""Черновик v1 — первая версия, сгенерированная ИИ (сохранена для отчёта, не используется)."""


class Leaderboard:
    def __init__(self):
        self.scores = {}

    def update_score(self, player, points):
        self.scores[player] = self.scores.get(player, 0) + points

    def top(self, k):
        return sorted(self.scores.items(), key=lambda x: x[1], reverse=True)[:k]
