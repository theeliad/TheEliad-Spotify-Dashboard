"""Read the playlists the user chose to track."""

from src.db.db import db_connection

_QUERY = "SELECT playlist_id FROM tracked_playlists ORDER BY tracked_at, playlist_id"


def load_tracked_playlist_ids() -> list[str]:
    """Return the tracked playlist ids in the order they were added."""
    with db_connection() as conn:
        return [row["playlist_id"] for row in conn.execute(_QUERY).fetchall()]
