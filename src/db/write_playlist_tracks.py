"""Replace the current-state track rows of one playlist."""

import sqlite3
from collections.abc import Sequence

from src.schemas import Track

_INSERT = """
INSERT OR REPLACE INTO playlist_tracks (
    playlist_id, track_uri, track_name, artists, album_name,
    added_at, added_by, position
) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
"""


def write_playlist_tracks(
    conn: sqlite3.Connection, playlist_id: str, tracks: Sequence[Track]
) -> None:
    """Replace the current-state track rows for one playlist."""
    conn.execute("DELETE FROM playlist_tracks WHERE playlist_id = ?", (playlist_id,))
    conn.executemany(
        _INSERT,
        [
            (
                playlist_id,
                track.track_uri,
                track.track_name,
                track.artists,
                track.album_name,
                track.added_at,
                track.added_by,
                track.position,
            )
            for track in tracks
        ],
    )
