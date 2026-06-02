from core.task_queue import TaskQueue

queue = TaskQueue()

queue.add_task(
    "research",
    {
        "description":
        "Vector Databases"
    }
)

queue.add_task(
    "research",
    {
        "description":
        "AI Agents"
    }
)

print(
    "Pending:",
    queue.pending_count()
)

task = queue.get_next_task()

print(task)