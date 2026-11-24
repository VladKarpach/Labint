import random
import sys
import threading
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from leaderboard import Entry, Leaderboard  # noqa: E402


def names(entries):
    return [e.player for e in entries]


class AddScoreTest(unittest.TestCase):
    def test_accumulates_and_returns_total(self):
        lb = Leaderboard()
        self.assertEqual(lb.add_score("alice", 10), 10)
        self.assertEqual(lb.add_score("alice", 5), 15)

    def test_nickname_is_normalized(self):
        lb = Leaderboard()
        lb.add_score("Neo", 5)
        lb.add_score("  neo ", 5)
        self.assertEqual(len(lb), 1)
        self.assertEqual(lb.top(1), [Entry(1, "Neo", 10)])  # первое написание

    def test_fullwidth_unicode_nickname_is_same_player(self):
        lb = Leaderboard()
        lb.add_score("Ｎeo", 5)  # первая буква — полноширинная латинская
        lb.add_score("neo", 5)
        self.assertEqual(len(lb), 1)

    def test_invalid_points(self):
        lb = Leaderboard()
        for bad in (0, -5):
            with self.assertRaises(ValueError):
                lb.add_score("alice", bad)
        for bad in (1.5, "5", None, True, float("nan")):
            with self.assertRaises(TypeError):
                lb.add_score("alice", bad)
        self.assertEqual(len(lb), 0)  # неудачные вызовы ничего не создают

    def test_invalid_nickname(self):
        lb = Leaderboard()
        for bad in ("", "   "):
            with self.assertRaises(ValueError):
                lb.add_score(bad, 1)
        with self.assertRaises(TypeError):
            lb.add_score(None, 1)


class TopTest(unittest.TestCase):
    def test_empty_board(self):
        self.assertEqual(Leaderboard().top(3), [])

    def test_sorted_by_score_desc_with_ranks(self):
        lb = Leaderboard()
        for nick, pts in [("alice", 10), ("bob", 30), ("carol", 20)]:
            lb.add_score(nick, pts)
        self.assertEqual(
            lb.top(3), [Entry(1, "bob", 30), Entry(2, "carol", 20), Entry(3, "alice", 10)]
        )

    def test_k_larger_than_players_returns_all(self):
        lb = Leaderboard()
        lb.add_score("alice", 10)
        lb.add_score("bob", 5)
        self.assertEqual(len(lb.top(100)), 2)

    def test_k_zero_returns_empty(self):
        lb = Leaderboard()
        lb.add_score("alice", 10)
        self.assertEqual(lb.top(0), [])

    def test_invalid_k(self):
        lb = Leaderboard()
        lb.add_score("alice", 10)
        with self.assertRaises(ValueError):
            lb.top(-1)
        for bad in (2.0, "2", None, True):
            with self.assertRaises(TypeError):
                lb.top(bad)

    def test_tie_earlier_reached_is_higher(self):
        lb = Leaderboard()
        lb.add_score("bob", 10)    # bob набрал 10 первым
        lb.add_score("alice", 10)
        self.assertEqual(names(lb.top(2)), ["bob", "alice"])

    def test_tie_depends_on_when_score_was_reached_not_on_insertion(self):
        lb = Leaderboard()
        lb.add_score("bob", 5)     # bob создан первым...
        lb.add_score("alice", 10)  # ...но alice набрала 10 раньше
        lb.add_score("bob", 5)     # bob дотянулся до 10 позже
        self.assertEqual(names(lb.top(2)), ["alice", "bob"])

    def test_three_way_tie_is_stable(self):
        lb = Leaderboard()
        for nick in ("c", "a", "b"):
            lb.add_score(nick * 3, 7)
        self.assertEqual(names(lb.top(3)), ["ccc", "aaa", "bbb"])

    def test_matches_brute_force_on_random_data(self):
        rng = random.Random(42)
        lb = Leaderboard()
        expected = {}
        for step in range(1, 2001):
            nick = f"player{rng.randrange(300)}"
            pts = rng.randrange(1, 50)
            lb.add_score(nick, pts)
            total, _ = expected.get(nick, (0, 0))
            expected[nick] = (total + pts, step)
        brute = sorted(expected.items(), key=lambda kv: (-kv[1][0], kv[1][1]))
        for k in (1, 5, 50, 300, 1000):
            self.assertEqual(
                [(e.player, e.score) for e in lb.top(k)],
                [(name, total) for name, (total, _) in brute[:k]],
            )


class RankAndResetTest(unittest.TestCase):
    def test_rank_of(self):
        lb = Leaderboard()
        lb.add_score("alice", 10)
        lb.add_score("bob", 30)
        self.assertEqual(lb.rank_of("BOB"), 1)
        self.assertEqual(lb.rank_of("alice"), 2)

    def test_rank_of_unknown_is_none(self):
        self.assertIsNone(Leaderboard().rank_of("nobody"))

    def test_rank_matches_top(self):
        lb = Leaderboard()
        for i, nick in enumerate(["a1", "b2", "c3", "d4"]):
            lb.add_score(nick, 10 * (i % 2 + 1))
        for entry in lb.top(4):
            self.assertEqual(lb.rank_of(entry.player), entry.rank)

    def test_reset(self):
        lb = Leaderboard()
        lb.add_score("alice", 10)
        lb.reset()
        self.assertEqual(len(lb), 0)
        self.assertEqual(lb.top(5), [])
        lb.add_score("bob", 1)
        self.assertEqual(lb.top(1), [Entry(1, "bob", 1)])


class ConcurrencyTest(unittest.TestCase):
    def test_parallel_updates_do_not_lose_points(self):
        lb = Leaderboard()
        old_interval = sys.getswitchinterval()
        sys.setswitchinterval(1e-6)  # частые переключения потоков повышают шанс гонки

        def worker():
            for _ in range(2000):
                lb.add_score("alice", 1)

        try:
            threads = [threading.Thread(target=worker) for _ in range(8)]
            for t in threads:
                t.start()
            for t in threads:
                t.join()
        finally:
            sys.setswitchinterval(old_interval)
        self.assertEqual(lb.top(1)[0].score, 16000)


if __name__ == "__main__":
    unittest.main()
