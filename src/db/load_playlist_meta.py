"""Read the latest recorded metadata snapshot for one playlist."""

from src.db.db import db_connection

_SELECT = (
    "SELECT owner_id, owner_display_name, follower_count, collaborative, "
    "snapshot_id, captured_at "
    "FROM playlist_meta_snapshots WHERE playlist_id = ? ORDER BY id DESC LIMIT 1"
)


def load_playlist_meta(playlist_id: str) -> dict | None:
    """Return the newest metadata snapshot for a playlist, or None."""
    with db_connection() as conn:
        row = conn.execute(_SELECT, (playlist_id,)).fetchone()
    return dict(row) if row is not None else None
