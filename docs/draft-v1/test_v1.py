"""Черновые тесты v1 — первая версия, сгенерированная ИИ (для отчёта)."""
import unittest

from leaderboard_v1 import Leaderboard


class TestLeaderboard(unittest.TestCase):
    def test_update_and_top(self):
        lb = Leaderboard()
        lb.update_score("alice", 10)
        lb.update_score("bob", 20)
        self.assertEqual(lb.top(1), [("bob", 20)])

    def test_tie(self):
        lb = Leaderboard()
        lb.update_score("alice", 10)
        lb.update_score("bob", 10)
        self.assertEqual(lb.top(2), [("alice", 10), ("bob", 10)])

    def test_k_larger_than_players(self):
        lb = Leaderboard()
        lb.update_score("alice", 10)
        self.assertEqual(lb.top(5), [("alice", 10)])

    def test_accumulates(self):
        lb = Leaderboard()
        lb.update_score("alice", 10)
        lb.update_score("alice", 5)
        self.assertEqual(lb.top(1), [("alice", 15)])


if __name__ == "__main__":
    unittest.main()
