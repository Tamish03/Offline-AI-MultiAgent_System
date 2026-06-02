from core.task_queue import TaskQueue
from workflows.queue_engine import QueueEngine

queue = TaskQueue()

queue.add_task(
    "research",
    {
        "description":
        "Vector Databases"
    }
)

engine = QueueEngine()

result = engine.process_next_task()

print(result)