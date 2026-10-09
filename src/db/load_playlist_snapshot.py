"""Read a playlist's last-seen snapshot id within a caller-owned transaction."""

import sqlite3


def load_playlist_snapshot(conn: sqlite3.Connection, playlist_id: str) -> str | None:
    """Return the stored snapshot id for one playlist, or None if unseen."""
    row = conn.execute(
        "SELECT snapshot_id FROM playlists WHERE playlist_id = ?", (playlist_id,)
    ).fetchone()
    return row["snapshot_id"] if row is not None else None
