"""Append plays recorded from the recently-played endpoint."""

import sqlite3
from collections.abc import Sequence

from src.schemas import PlayEvent

_INSERT = """
INSERT OR IGNORE INTO play_events (track_uri, track_name, artists, played_at)
VALUES (?, ?, ?, ?)
"""


def write_play_events(conn: sqlite3.Connection, events: Sequence[PlayEvent]) -> int:
    """Append play events, skipping plays already recorded, and return attempted count."""
    conn.executemany(
        _INSERT,
        [
            (event.track_uri, event.track_name, event.artists, event.played_at)
            for event in events
        ],
    )
    return len(events)