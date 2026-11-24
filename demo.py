"""Небольшая демонстрация: python demo.py"""
from leaderboard import Leaderboard

lb = Leaderboard()
for nick, pts in [("Neo", 250), ("Trinity", 400), ("Morpheus", 250), ("neo", 100)]:
    lb.add_score(nick, pts)

print("Топ-3:")
for e in lb.top(3):
    print(f"  {e.rank}. {e.player}: {e.score}")
print("Место Morpheus:", lb.rank_of("morpheus"))
print("Игрок Smith:", lb.rank_of("Smith"))
