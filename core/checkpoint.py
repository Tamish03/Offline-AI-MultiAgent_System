import sqlite3
import json


class CheckpointManager:

    def __init__(
        self,
        db_name="data/checkpoints.db"
    ):

        self.conn = sqlite3.connect(
            db_name,
            check_same_thread=False
        )

        self.create_table()

    def create_table(self):

        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS checkpoints (

            job_id TEXT,

            step INTEGER,

            step_name TEXT,

            output TEXT,

            PRIMARY KEY(job_id, step)

        )
        """)

        self.conn.commit()

    def save_checkpoint(
        self,
        job_id,
        step,
        step_name,
        output
    ):

        self.conn.execute(
            """
            INSERT OR REPLACE INTO checkpoints
            VALUES (?, ?, ?, ?)
            """,
            (
                job_id,
                step,
                step_name,
                json.dumps(output)
            )
        )

        self.conn.commit()

    def load_checkpoints(
        self,
        job_id
    ):

        cursor = self.conn.execute(
            """
            SELECT step, step_name, output
            FROM checkpoints
            WHERE job_id=?
            ORDER BY step
            """,
            (job_id,)
        )

        rows = cursor.fetchall()

        results = []

        for row in rows:

            results.append({
                "step": row[0],
                "step_name": row[1],
                "output": json.loads(row[2])
            })

        return results

    def get_last_step(
        self,
        job_id
    ):

        cursor = self.conn.execute(
            """
            SELECT MAX(step)
            FROM checkpoints
            WHERE job_id=?
            """,
            (job_id,)
        )

        result = cursor.fetchone()[0]

        return result or 0