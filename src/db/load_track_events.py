"""Read the append-only change log from SQLite."""

import pandas as pd

from src.db.db import db_connection

_SELECT = (
    "SELECT id, playlist_id, track_uri, track_name, artists, "
    "added_at, added_by, change_type, detected_at FROM track_events"
)


def load_track_events(
    playlist_id: str | None = None,
    limit: int | None = None,
) -> pd.DataFrame:
    """Return the event log, newest first, with optional filters."""
    conditions: list[str] = []
    params: list[object] = []
    if playlist_id is not None:
        conditions.append("playlist_id = ?")
        params.append(playlist_id)
    query = _SELECT
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    query += " ORDER BY detected_at DESC, id DESC"
    if limit is not None:
        query += " LIMIT ?"
        params.append(limit)
    with db_connection() as conn:
        return pd.read_sql_query(query, conn, params=tuple(params))
