import pytest

from pomodoro import Config, Pomodoro, State, schedule


def test_initial_state_is_work():
    timer = Pomodoro()
    assert timer.state is State.WORK
    assert timer.completed_sessions == 0
    assert timer.duration == 25


def test_work_is_followed_by_short_break():
    timer = Pomodoro()
    assert timer.next() is State.SHORT_BREAK
    assert timer.duration == 5
    assert timer.completed_sessions == 1


def test_break_is_followed_by_work():
    timer = Pomodoro()
    timer.next()  # короткий перерыв
    assert timer.next() is State.WORK


def test_long_break_after_fourth_session():
    timer = Pomodoro()
    states = [timer.next() for _ in range(8)]  # 4 пары «работа -> перерыв»
    # результаты next(): перерыв, работа, перерыв, работа, перерыв, работа, ДЛИННЫЙ, работа
    assert states[6] is State.LONG_BREAK
    assert states[:6] == [
        State.SHORT_BREAK, State.WORK,
        State.SHORT_BREAK, State.WORK,
        State.SHORT_BREAK, State.WORK,
    ]


def test_long_break_duration():
    timer = Pomodoro()
    for _ in range(7):
        timer.next()
    assert timer.state is State.LONG_BREAK
    assert timer.duration == 15


def test_work_follows_long_break():
    timer = Pomodoro()
    for _ in range(8):
        timer.next()
    assert timer.state is State.WORK
    assert timer.completed_sessions == 4


def test_long_break_repeats_every_cycle():
    timer = Pomodoro()
    long_breaks = 0
    for _ in range(16):  # 8 сессий
        if timer.next() is State.LONG_BREAK:
            long_breaks += 1
    assert long_breaks == 2


def test_custom_config_changes_cycle():
    timer = Pomodoro(Config(work=50, short_break=10, long_break=30, sessions_before_long=2))
    assert timer.duration == 50
    timer.next()
    assert timer.state is State.SHORT_BREAK and timer.duration == 10
    timer.next()
    timer.next()
    assert timer.state is State.LONG_BREAK and timer.duration == 30


def test_reset_returns_to_start():
    timer = Pomodoro()
    for _ in range(5):
        timer.next()
    timer.reset()
    assert timer.state is State.WORK
    assert timer.completed_sessions == 0


@pytest.mark.parametrize(
    "kwargs",
    [
        {"work": 0},
        {"short_break": -1},
        {"long_break": 0},
        {"sessions_before_long": 0},
    ],
)
def test_invalid_config_raises(kwargs):
    with pytest.raises(ValueError):
        Config(**kwargs)


def test_schedule_for_one_cycle():
    plan = schedule(4)
    assert len(plan) == 8
    assert plan[-1] == (State.LONG_BREAK, 15)
    assert sum(minutes for _, minutes in plan) == 4 * 25 + 3 * 5 + 15


def test_schedule_invalid_sessions():
    with pytest.raises(ValueError):
        schedule(0)
