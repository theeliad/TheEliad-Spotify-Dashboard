"""Record a playlist the user chose to track. Append-only."""

from src.db.db import db_connection

_INSERT = "INSERT OR IGNORE INTO tracked_playlists (playlist_id) VALUES (?)"


def write_tracked_playlist(playlist_id: str) -> None:
    """Track a playlist id, ignoring it if it is already tracked."""
    with db_connection() as conn:
        conn.execute(_INSERT, (playlist_id,))
