"""Start a poll-run bookkeeping row."""

import sqlite3


def start_poll_run(conn: sqlite3.Connection, started_at: str) -> int:
    """Insert a poll_runs row and return its id."""
    cursor = conn.execute("INSERT INTO poll_runs (started_at) VALUES (?)", (started_at,))
    return int(cursor.lastrowid)
