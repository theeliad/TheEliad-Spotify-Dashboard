"""Read cached Spotify user display names."""

from src.db.db import db_connection

_SELECT = "SELECT user_id, display_name FROM app_users"


def load_app_users() -> dict[str, str]:
    """Return a mapping of user id to cached display name."""
    with db_connection() as conn:
        rows = conn.execute(_SELECT).fetchall()
    return {row["user_id"]: row["display_name"] or row["user_id"] for row in rows}
