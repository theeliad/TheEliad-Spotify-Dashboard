"""Record the outcome of a poll run."""

import sqlite3


def finish_poll_run(
    conn: sqlite3.Connection,
    run_id: int,
    playlists_seen: int,
    events_added: int,
    error: str | None,
) -> None:
    """Update a poll_runs row with its final outcome."""
    conn.execute(
        "UPDATE poll_runs SET finished_at = datetime('now'), playlists_seen = ?, "
        "events_added = ?, error = ? WHERE id = ?",
        (playlists_seen, events_added, error, run_id),
    )
