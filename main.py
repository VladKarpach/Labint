from typing import Dict, List


def create_task(tasks: Dict[int, dict], task_id: int, text: str, priority: int) -> None:
    if priority not in (1, 2, 3):
        raise ValueError("priority must be 1..3")
    if task_id in tasks:
        raise ValueError("id exists")
    tasks[task_id] = {"text": text, "priority": priority, "status": "open"}


def close_task(tasks: Dict[int, dict], task_id: int) -> None:
    if task_id not in tasks:
        raise KeyError("task not found")
    tasks[task_id]["status"] = "closed"


def open_tasks(tasks: Dict[int, dict]) -> List[int]:
    return sorted(i for i, t in tasks.items() if t["status"] == "open")


def filter_by_priority(tasks: Dict[int, dict], priority: int) -> List[int]:
    return sorted(i for i, t in tasks.items() if t["priority"] == priority)


def count_closed(tasks: Dict[int, dict]) -> int:
    return sum(1 for t in tasks.values() if t["status"] == "closed")
