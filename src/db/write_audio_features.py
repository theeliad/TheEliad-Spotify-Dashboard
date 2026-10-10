"""Persist cached tempo and duration for tracks."""

import sqlite3
from collections.abc import Sequence

from src.schemas import AudioFeature

_UPSERT = """
INSERT INTO audio_features_cache (track_uri, tempo, duration_ms)
VALUES (?, ?, ?)
ON CONFLICT(track_uri) DO UPDATE SET
    tempo = excluded.tempo,
    duration_ms = excluded.duration_ms
"""


def write_audio_features(
    conn: sqlite3.Connection, features: Sequence[AudioFeature]
) -> None:
    """Upsert tempo and duration rows for the given tracks."""
    conn.executemany(
        _UPSERT,
        [(feature.track_uri, feature.tempo, feature.duration_ms) for feature in features],
    )
