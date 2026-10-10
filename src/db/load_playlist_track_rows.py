"""Read current playlist tracks as domain objects within a caller-owned transaction."""

import sqlite3

from src.schemas import Track

_QUERY = (
    "SELECT track_uri, track_name, artists, album_name, added_at, added_by, position, popularity "
    "FROM playlist_tracks WHERE playlist_id = ? ORDER BY position"
)


def load_playlist_track_rows(conn: sqlite3.Connection, playlist_id: str) -> list[Track]:
    """Return the stored tracks of one playlist ordered by position."""
    rows = conn.execute(_QUERY, (playlist_id,)).fetchall()
    return [
        Track(
            track_uri=row["track_uri"],
            track_name=row["track_name"] or "",
            artists=row["artists"] or "",
            album_name=row["album_name"] or "",
            added_at=row["added_at"],
            added_by=row["added_by"],
            position=row["position"] if row["position"] is not None else 0,
            popularity=row["popularity"],
        )
        for row in rows
    ]
