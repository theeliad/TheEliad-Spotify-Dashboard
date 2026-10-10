"""Read plays of the selected playlist's tracks, ranked by our measured listens."""

import pandas as pd

from src.db.db import db_connection

_QUERY = (
    "SELECT pt.track_uri, pt.track_name, pt.artists, pt.popularity, "
    "COALESCE(pe.play_count, 0) AS play_count "
    "FROM playlist_tracks AS pt "
    "LEFT JOIN ("
    "    SELECT track_uri, COUNT(*) AS play_count FROM play_events GROUP BY track_uri"
    ") AS pe ON pe.track_uri = pt.track_uri "
    "WHERE pt.playlist_id = ? "
    "ORDER BY play_count DESC, pt.popularity DESC"
)


def load_playlist_plays(playlist_id: str) -> pd.DataFrame:
    """Return the selected playlist's tracks with play counts and popularity."""
    with db_connection() as conn:
        return pd.read_sql_query(_QUERY, conn, params=(playlist_id,))