"""Append change events to the immutable log."""

import sqlite3
from collections.abc import Sequence

from src.schemas import TrackEvent

_INSERT = """
INSERT INTO track_events (
    playlist_id, track_uri, track_name, artists,
    added_at, added_by, change_type
) VALUES (?, ?, ?, ?, ?, ?, ?)
"""


def write_track_events(conn: sqlite3.Connection, events: Sequence[TrackEvent]) -> int:
    """Append change events and return the number written."""
    conn.executemany(
        _INSERT,
        [
            (
                event.playlist_id,
                event.track_uri,
                event.track_name,
                event.artists,
                event.added_at,
                event.added_by,
                event.change_type,
            )
            for event in events
        ],
    )
    return len(events)
