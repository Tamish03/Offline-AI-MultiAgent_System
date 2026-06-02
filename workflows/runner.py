import time

from core.task_queue import TaskQueue
from workflows.engine import WorkflowEngine


class WorkflowRunner:

    def __init__(self):

        self.queue = TaskQueue()

        self.engine = WorkflowEngine()

    def run_forever(self):

        print("\n" + "=" * 60)
        print("AI OS RUNNER STARTED")
        print("=" * 60)

        while True:

            try:

                task = (
                    self.queue
                    .get_next_task()
                )

                if not task:

                    time.sleep(1)

                    continue

                print(
                    f"\nFound Task:\n{task}"
                )

                task_type = task[
                    "task_type"
                ]

                print(
                    f"\nTask Type: {task_type}"
                )

                if task_type != "goal":

                    print(
                        f"\nUnknown task type: "
                        f"{task_type}"
                    )

                    self.queue.mark_failed(
                        task["id"]
                    )

                    continue

                self.queue.mark_running(
                    task["id"]
                )

                goal = task[
                    "payload"
                ].get(
                    "goal",
                    ""
                )

                print(
                    f"\nProcessing Goal:\n"
                    f"{goal}\n"
                )

                result = (
                    self.engine
                    .execute_goal(
                        goal,
                        task["id"]
                    )
                )

                self.queue.mark_completed(
                    task["id"],
                    output_file=result.get("file")
                )

                print(
                    "\n" + "=" * 60
                )

                print(
                    "TASK COMPLETED SUCCESSFULLY"
                )

                print(
                    "=" * 60
                )

                intent = result.get(
                    "intent",
                    "UNKNOWN"
                )

                print(
                    f"\nIntent: {intent}"
                )

               

                if intent == "TOOL":

                    print(
                        "\nTOOL RESULT:"
                    )

                    print(
                        "-" * 50
                    )

                    print(
                        result.get(
                            "output",
                            ""
                        )
                    )

                    print(
                        "-" * 50
                    )

              

                elif intent == "RESPOND":

                    print(
                        "\nOUTPUT:"
                    )

                    print(
                        "-" * 50
                    )

                    print(
                        result.get(
                            "output",
                            ""
                        )
                    )

                    print(
                        "-" * 50
                    )

                    print(
                        "\nSaved To:"
                    )

                    print(
                        result.get(
                            "file",
                            "No file generated"
                        )
                    )

           

                elif intent == "CONTENT":

                    print(
                        "\nCONTENT GENERATED:"
                    )

                    print(
                        "-" * 50
                    )

                    print(
                        result.get(
                            "output",
                            ""
                        )
                    )

                    print(
                        "-" * 50
                    )

                    print(
                        "\nSaved To:"
                    )

                    print(
                        result.get(
                            "file",
                            "No file generated"
                        )
                    )

                

                elif intent == "QUESTION":

                    print(
                        "\nANSWER GENERATED:"
                    )

                    print(
                        "-" * 50
                    )

                    print(
                        result.get(
                            "output",
                            ""
                        )
                    )

                    print(
                        "-" * 50
                    )

                    print(
                        "\nSaved To:"
                    )

                    print(
                        result.get(
                            "file",
                            "No file generated"
                        )
                    )


                elif intent == "WORKFLOW":

                    print(
                        "\nWorkflow completed."
                    )

                    print(
                        "\nOutput File:"
                    )

                    print(
                        result.get(
                            "file",
                            "No file generated"
                        )
                    )

                else:

                    print(
                        "\nUnknown intent received."
                    )

                print(
                    "\nQueue Status:"
                )

                print(
                    f"Pending: "
                    f"{self.queue.pending_count()}"
                )

                print(
                    f"Running: "
                    f"{self.queue.running_count()}"
                )

                print(
                    f"Completed: "
                    f"{self.queue.completed_count()}"
                )

                print(
                    f"Failed: "
                    f"{self.queue.failed_count()}"
                )

            except Exception as e:

                try:

                    if (
                        "task" in locals()
                        and task
                    ):

                        self.queue.mark_failed(
                            task["id"]
                        )

                except Exception:

                    pass

                print(
                    "\n" + "=" * 60
                )

                print(
                    "ERROR"
                )

                print(
                    "=" * 60
                )

                print(
                    str(e)
                )

                time.sleep(2)
