class Task:
    def __init__(self, task_id, text, priority):
        self.id = task_id
        self.text = text
        self.priority = priority
        self.closed = False

    def close(self):
        self.closed = True

    def __str__(self):
        status = "закрыта" if self.closed else "открыта"
        return f"#{self.id} [{self.priority}] {self.text} ({status})"


class TaskManager:
    def __init__(self):
        self._tasks = []
        self._next_id = 1

    def create(self, text, priority):
        if priority not in (1, 2, 3):
            raise ValueError("Приоритет должен быть 1, 2 или 3")
        task = Task(self._next_id, text, priority)
        self._tasks.append(task)
        self._next_id += 1
        return task.id

    def close(self, task_id):
        for t in self._tasks:
            if t.id == task_id:
                t.close()
                return True
        return False

    def open_tasks(self):
        return [t for t in self._tasks if not t.closed]

    def by_priority(self, priority):
        return [t for t in self._tasks if t.priority == priority and not t.closed]

    def closed_count(self):
        return sum(1 for t in self._tasks if t.closed)


def print_tasks(title, items):
    print(f"\n--- {title} ---")
    if not items:
        print("(пусто)")
    for t in items:
        print(t)


# Демонстрационный сценарий
if __name__ == "__main__":
    manager = TaskManager()
    manager.create("задача 1,,,", 2)
    manager.create("Сделать лабу", 1)
    manager.create("понять лекцию", 3)
    manager.create("сходить в уник", 2)

    manager.close(1)

    print_tasks("Все открытые", manager.open_tasks())
    print_tasks("Приоритет 2", manager.by_priority(2))
    print(f"\nЗакрытых задач: {manager.closed_count()}")