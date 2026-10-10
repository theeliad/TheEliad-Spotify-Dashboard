"""Read the current tracks of one playlist from SQLite."""

import pandas as pd

from src.db.db import db_connection

_QUERY = (
    "SELECT pt.track_uri, pt.track_name, pt.artists, pt.album_name, pt.added_at, "
    "pt.added_by, pt.position, pt.popularity, af.tempo "
    "FROM playlist_tracks AS pt "
    "LEFT JOIN audio_features_cache AS af ON af.track_uri = pt.track_uri "
    "WHERE pt.playlist_id = ? ORDER BY pt.position"
)


def load_playlist_tracks(playlist_id: str) -> pd.DataFrame:
    """Return the current tracks of one playlist ordered by position."""
    with db_connection() as conn:
        return pd.read_sql_query(_QUERY, conn, params=(playlist_id,))


def earliest_added_at(playlist_id: str) -> str | None:
    """Return the playlist's earliest known added_at among current tracks, or None."""
    with db_connection() as conn:
        row = conn.execute(
            "SELECT MIN(added_at) AS created FROM playlist_tracks "
            "WHERE playlist_id = ? AND added_at IS NOT NULL",
            (playlist_id,),
        ).fetchone()
    return row["created"] if row is not None and row["created"] else None
