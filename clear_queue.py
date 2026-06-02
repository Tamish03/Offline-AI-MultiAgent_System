# clear_queue.py

import sqlite3

conn = sqlite3.connect("data/queue.db")

conn.execute("DELETE FROM tasks")

conn.commit()

conn.close()

print("Queue cleared successfully.")