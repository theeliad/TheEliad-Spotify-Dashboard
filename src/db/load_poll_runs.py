"""Read poll-run bookkeeping from SQLite."""

import pandas as pd

from src.db.db import db_connection

_QUERY = (
    "SELECT id, started_at, finished_at, playlists_seen, events_added, error "
    "FROM poll_runs ORDER BY id DESC LIMIT ?"
)


def load_poll_runs(limit: int = 20) -> pd.DataFrame:
    """Return the most recent poll runs, newest first."""
    with db_connection() as conn:
        return pd.read_sql_query(_QUERY, conn, params=(limit,))
