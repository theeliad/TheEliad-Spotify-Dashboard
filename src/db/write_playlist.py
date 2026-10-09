"""Upsert a playlist's last-seen snapshot."""

import sqlite3

from src.schemas import Playlist

_UPSERT = """
INSERT INTO playlists (
    playlist_id, name, owner_id, collaborative, snapshot_id,
    track_count, first_seen_at, last_polled_at
) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
ON CONFLICT(playlist_id) DO UPDATE SET
    name = excluded.name,
    owner_id = excluded.owner_id,
    collaborative = excluded.collaborative,
    snapshot_id = excluded.snapshot_id,
    track_count = excluded.track_count,
    last_polled_at = excluded.last_polled_at
"""


def write_playlist(conn: sqlite3.Connection, playlist: Playlist, polled_at: str) -> None:
    """Insert or update the current playlist row, preserving first_seen_at."""
    conn.execute(
        _UPSERT,
        (
            playlist.playlist_id,
            playlist.name,
            playlist.owner_id,
            int(playlist.collaborative),
            playlist.snapshot_id,
            playlist.track_count,
            polled_at,
            polled_at,
        ),
    )
