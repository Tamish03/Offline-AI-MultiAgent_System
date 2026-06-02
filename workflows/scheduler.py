from core.task_queue import TaskQueue


class Scheduler:

    def __init__(
        self,
        scheduling_window=0
    ):

        self.queue = TaskQueue()

        self.scheduling_window = (
            scheduling_window
        )

    def get_next_scheduled_task(self):
        """
        Return next pending task immediately.

        No artificial delay.
        Priority ordering is handled
        by TaskQueue.get_next_task().
        """

        task = self.queue.get_next_task()

        return task