"""Read the current playlist state from SQLite."""

import pandas as pd

from src.db.db import db_connection

_QUERY = (
    "SELECT playlist_id, name, owner_id, collaborative, snapshot_id, "
    "track_count, first_seen_at, last_polled_at FROM playlists ORDER BY name"
)


def load_playlists() -> pd.DataFrame:
    """Return all playlists ordered by name."""
    with db_connection() as conn:
        return pd.read_sql_query(_QUERY, conn)
