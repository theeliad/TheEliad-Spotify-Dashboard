"""Persist a known Spotify user's display name."""

from src.db.db import db_connection

_UPSERT = """
INSERT INTO app_users (user_id, display_name, fetched_at)
VALUES (?, ?, datetime('now'))
ON CONFLICT(user_id) DO UPDATE SET
    display_name = excluded.display_name,
    fetched_at = excluded.fetched_at
"""


def write_app_user(user_id: str, display_name: str) -> None:
    """Insert or refresh a user's cached display name."""
    with db_connection() as conn:
        conn.execute(_UPSERT, (user_id, display_name))
