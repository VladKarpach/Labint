"""Логика интервалов таймера «Помодоро».

Цикл: работа -> короткий перерыв -> работа -> ... После каждой
`sessions_before_long`-й рабочей сессии вместо короткого перерыва
наступает длинный. После любого перерыва снова начинается работа.
"""
from dataclasses import dataclass
from enum import Enum


class State(Enum):
    WORK = "work"
    SHORT_BREAK = "short_break"
    LONG_BREAK = "long_break"


@dataclass(frozen=True)
class Config:
    """Длительности (в минутах) и частота длинного перерыва."""

    work: int = 25
    short_break: int = 5
    long_break: int = 15
    sessions_before_long: int = 4

    def __post_init__(self):
        for name in ("work", "short_break", "long_break", "sessions_before_long"):
            if getattr(self, name) <= 0:
                raise ValueError(f"{name} должно быть положительным числом")


class Pomodoro:
    """Конечный автомат интервалов помодоро."""

    def __init__(self, config=None):
        self.config = config or Config()
        self.state = State.WORK
        self.completed_sessions = 0

    @property
    def duration(self):
        """Длительность текущего интервала в минутах."""
        return {
            State.WORK: self.config.work,
            State.SHORT_BREAK: self.config.short_break,
            State.LONG_BREAK: self.config.long_break,
        }[self.state]

    def next(self):
        """Завершить текущий интервал и перейти к следующему."""
        if self.state is State.WORK:
            self.completed_sessions += 1
            if self.completed_sessions % self.config.sessions_before_long == 0:
                self.state = State.LONG_BREAK
            else:
                self.state = State.SHORT_BREAK
        else:
            self.state = State.WORK
        return self.state

    def reset(self):
        """Вернуться в начальное состояние."""
        self.state = State.WORK
        self.completed_sessions = 0


def schedule(sessions, config=None):
    """План на `sessions` рабочих сессий: список (состояние, минуты).

    После каждой рабочей сессии идёт перерыв (в том числе после последней).
    """
    if sessions <= 0:
        raise ValueError("sessions должно быть положительным числом")
    timer = Pomodoro(config)
    plan = []
    for _ in range(sessions):
        plan.append((timer.state, timer.duration))
        timer.next()
        plan.append((timer.state, timer.duration))
        timer.next()
    return plan
