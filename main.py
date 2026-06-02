from core.task_queue import TaskQueue

queue = TaskQueue()

print("\n=== AI OS Goal Submission ===\n")

goal = input(
    "Enter your goal:\n\n"
)

priority = int(
    input(
        "\nPriority (1-10): "
    )
)

queue.add_task(
    "goal",
    {
        "goal": goal
    },
    priority=priority
)

print(
    "\nGoal submitted successfully."
)