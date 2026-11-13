
tasks = []

def create_task(text, priority):
    """Создаёт задачу и добавляет её в список. Возвращает id."""
    if priority not in (1, 2, 3):
        raise ValueError("Приоритет должен быть 1, 2 или 3")
    task = {
        "id": len(tasks) + 1,
        "text": text,
        "priority": priority,
        "closed": False,
    }
    tasks.append(task)
    return task["id"]


def close_task(task_id):
    """Закрывает задачу по id. Возвращает True, если получилось."""
    for t in tasks:
        if t["id"] == task_id:
            t["closed"] = True
            return True
    return False


def list_open():
    """Список открытых задач."""
    return [t for t in tasks if not t["closed"]]


def filter_by_priority(priority):
    """Открытые задачи с заданным приоритетом."""
    return [t for t in tasks if t["priority"] == priority and not t["closed"]]


def count_closed():
    """Количество закрытых задач."""
    return sum(1 for t in tasks if t["closed"])


def print_tasks(title, items):
    print(f"\n--- {title} ---")
    if not items:
        print("(пусто)")
    for t in items:
        status = "закрыта" if t["closed"] else "открыта"
        print(f'#{t["id"]} [{t["priority"]}] {t["text"]} ({status})')


# Демонстрационный сценарий
if __name__ == "__main__":
    create_task("задача 1,,,", 2)
    create_task("Сделать лабу", 1)
    create_task("понять лекцию", 3)
    create_task("сходить в уник", 2)

    close_task(1)  # закрываем первую задачу

    print_tasks("Все открытые", list_open())
    print_tasks("Приоритет 2", filter_by_priority(2))
    print(f"\nЗакрытых задач: {count_closed()}")