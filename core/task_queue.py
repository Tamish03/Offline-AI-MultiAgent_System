import sqlite3
import json
import uuid


class TaskQueue:

    def __init__(
        self,
        db_name="data/queue.db"
    ):

        self.conn = sqlite3.connect(
            db_name,
            check_same_thread=False
        )

        self.conn.row_factory = sqlite3.Row

        self.create_table()

        self.reset_stuck_tasks()

    def create_table(self):

        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (

            id TEXT PRIMARY KEY,

            task_type TEXT,

            payload TEXT,

            priority INTEGER DEFAULT 5,

            status TEXT DEFAULT 'pending',

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )
        """)

        self.conn.commit()

        # Add output_file column dynamically to existing tables
        try:
            self.conn.execute("ALTER TABLE tasks ADD COLUMN output_file TEXT")
            self.conn.commit()
        except sqlite3.OperationalError:
            pass

    def reset_stuck_tasks(self):

        """
        When AI OS restarts,
        convert old running tasks
        back to pending.
        """

        self.conn.execute(
            """
            UPDATE tasks
            SET status='pending'
            WHERE status='running'
            """
        )

        self.conn.commit()

    def add_task(
        self,
        task_type,
        payload,
        priority=5
    ):

        task_id = str(uuid.uuid4())

        self.conn.execute(
            """
            INSERT INTO tasks
            (
                id,
                task_type,
                payload,
                priority,
                status,
                created_at
            )
            VALUES
            (
                ?,
                ?,
                ?,
                ?,
                'pending',
                CURRENT_TIMESTAMP
            )
            """,
            (
                task_id,
                task_type,
                json.dumps(payload),
                priority
            )
        )

        self.conn.commit()

        return task_id

    def get_next_task(self):

        cursor = self.conn.execute(
            """
            SELECT
                id,
                task_type,
                payload,
                priority,
                status

            FROM tasks

            WHERE status='pending'

            ORDER BY
                priority DESC,
                created_at ASC

            LIMIT 1
            """
        )

        row = cursor.fetchone()

        if not row:

            return None

        return {
            "id": row["id"],
            "task_type": row["task_type"],
            "payload": json.loads(
                row["payload"]
            ),
            "priority": row["priority"],
            "status": row["status"]
        }

    def mark_running(
        self,
        task_id
    ):

        self.conn.execute(
            """
            UPDATE tasks
            SET status='running'
            WHERE id=?
            """,
            (task_id,)
        )

        self.conn.commit()

    def mark_completed(
        self,
        task_id,
        output_file=None
    ):

        self.conn.execute(
            """
            UPDATE tasks
            SET status='completed', output_file=?
            WHERE id=?
            """,
            (output_file, task_id)
        )

        self.conn.commit()

    def mark_failed(
        self,
        task_id
    ):

        self.conn.execute(
            """
            UPDATE tasks
            SET status='failed'
            WHERE id=?
            """,
            (task_id,)
        )

        self.conn.commit()

    def get_task_status(
        self,
        task_id
    ):

        cursor = self.conn.execute(
            """
            SELECT status
            FROM tasks
            WHERE id=?
            """,
            (task_id,)
        )

        row = cursor.fetchone()

        if row:

            return row["status"]

        return None

    def count_by_status(
        self,
        status
    ):

        cursor = self.conn.execute(
            """
            SELECT COUNT(*)
            FROM tasks
            WHERE status=?
            """,
            (status,)
        )

        return cursor.fetchone()[0]

    def pending_count(self):

        return self.count_by_status(
            "pending"
        )

    def running_count(self):

        return self.count_by_status(
            "running"
        )

    def completed_count(self):

        return self.count_by_status(
            "completed"
        )

    def failed_count(self):

        return self.count_by_status(
            "failed"
        )

    def get_all_tasks(self):

        cursor = self.conn.execute(
            """
            SELECT
                id,
                task_type,
                payload,
                priority,
                status,
                created_at,
                output_file
            FROM tasks
            ORDER BY created_at DESC
            """
        )

        tasks = []

        for row in cursor.fetchall():

            tasks.append(
                {
                    "id": row["id"],
                    "task_type": row["task_type"],
                    "payload": json.loads(
                        row["payload"]
                    ),
                    "priority": row["priority"],
                    "status": row["status"],
                    "created_at": row["created_at"],
                    "output_file": row["output_file"]
                }
            )

        return tasks