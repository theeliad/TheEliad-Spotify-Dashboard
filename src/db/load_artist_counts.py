"""Read the most frequent artists across current playlist tracks."""

import pandas as pd

from src.db.db import db_connection

_QUERY = (
    "SELECT artists, COUNT(*) AS track_count FROM playlist_tracks "
    "WHERE artists <> '' GROUP BY artists ORDER BY track_count DESC, artists LIMIT ?"
)


def load_artist_counts(limit: int = 15) -> pd.DataFrame:
    """Return the most frequent artists across all current playlist tracks."""
    with db_connection() as conn:
        return pd.read_sql_query(_QUERY, conn, params=(limit,))
