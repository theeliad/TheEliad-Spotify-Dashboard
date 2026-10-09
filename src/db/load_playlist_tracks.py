"""Read the current tracks of one playlist from SQLite."""

import pandas as pd

from src.db.db import db_connection

_QUERY = (
    "SELECT track_uri, track_name, artists, album_name, added_at, added_by, position "
    "FROM playlist_tracks WHERE playlist_id = ? ORDER BY position"
)


def load_playlist_tracks(playlist_id: str) -> pd.DataFrame:
    """Return the current tracks of one playlist ordered by position."""
    with db_connection() as conn:
        return pd.read_sql_query(_QUERY, conn, params=(playlist_id,))
