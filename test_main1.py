import pytest

from main import create_task, close_task, open_tasks, filter_by_priority, count_closed


# ---- create_task ----

def test_create_task():
    tasks = {}
    create_task(tasks, 1, "learn python", 2)
    assert tasks[1] == {"text": "learn python", "priority": 2, "status": "open"}


def test_create_task_priority_1_and_3():
    tasks = {}
    create_task(tasks, 1, "a", 1)
    create_task(tasks, 2, "b", 3)
    assert tasks[1]["priority"] == 1
    assert tasks[2]["priority"] == 3


def test_create_task_bad_priority_low():
    tasks = {}
    with pytest.raises(ValueError):
        create_task(tasks, 1, "a", 0)


def test_create_task_bad_priority_high():
    tasks = {}
    with pytest.raises(ValueError):
        create_task(tasks, 1, "a", 4)


def test_create_task_duplicate_id():
    tasks = {}
    create_task(tasks, 1, "a", 1)
    with pytest.raises(ValueError):
        create_task(tasks, 1, "b", 2)
    assert tasks[1]["text"] == "a"


# ---- close_task ----

def test_close_task():
    tasks = {}
    create_task(tasks, 1, "a", 1)
    close_task(tasks, 1)
    assert tasks[1]["status"] == "closed"


def test_close_task_twice():
    tasks = {}
    create_task(tasks, 1, "a", 1)
    close_task(tasks, 1)
    close_task(tasks, 1)
    assert tasks[1]["status"] == "closed"


def test_close_task_not_found():
    with pytest.raises(KeyError):
        close_task({}, 5)


# ---- open_tasks ----

def test_open_tasks_empty():
    assert open_tasks({}) == []


def test_open_tasks_sorted():
    tasks = {}
    create_task(tasks, 3, "c", 1)
    create_task(tasks, 1, "a", 1)
    create_task(tasks, 2, "b", 1)
    assert open_tasks(tasks) == [1, 2, 3]


def test_open_tasks_without_closed():
    tasks = {}
    create_task(tasks, 1, "a", 1)
    create_task(tasks, 2, "b", 1)
    close_task(tasks, 1)
    assert open_tasks(tasks) == [2]


# ---- filter_by_priority ----

def test_filter_by_priority():
    tasks = {}
    create_task(tasks, 2, "a", 1)
    create_task(tasks, 1, "b", 1)
    create_task(tasks, 3, "c", 2)
    assert filter_by_priority(tasks, 1) == [1, 2]


def test_filter_by_priority_no_match():
    tasks = {}
    create_task(tasks, 1, "a", 1)
    assert filter_by_priority(tasks, 3) == []


def test_filter_by_priority_empty():
    assert filter_by_priority({}, 1) == []


# ---- count_closed ----

def test_count_closed_empty():
    assert count_closed({}) == 0


def test_count_closed():
    tasks = {}
    create_task(tasks, 1, "a", 1)
    create_task(tasks, 2, "b", 2)
    create_task(tasks, 3, "c", 3)
    close_task(tasks, 1)
    close_task(tasks, 3)
    assert count_closed(tasks) == 2
