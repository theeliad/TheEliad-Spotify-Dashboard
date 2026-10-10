"""Read the most frequent artists among a playlist's current tracks."""

import pandas as pd

from src.db.db import db_connection


def load_artist_counts(limit: int = 15, playlist_id: str | None = None) -> pd.DataFrame:
    """Return the most frequent artists, optionally scoped to one playlist."""
    conditions = ["artists <> ''"]
    params: list[object] = []
    if playlist_id is not None:
        conditions.append("playlist_id = ?")
        params.append(playlist_id)
    query = (
        "SELECT artists, COUNT(*) AS track_count FROM playlist_tracks "
        f"WHERE {' AND '.join(conditions)} "
        "GROUP BY artists ORDER BY track_count DESC, artists LIMIT ?"
    )
    params.append(limit)
    with db_connection() as conn:
        return pd.read_sql_query(query, conn, params=tuple(params))
