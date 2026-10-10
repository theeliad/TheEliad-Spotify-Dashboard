"""Read playlist tracks that have no cached audio features yet."""

import sqlite3

from src.schemas import Track

_QUERY = (
    "SELECT pt.track_uri, "
    "MIN(pt.track_name) AS track_name, "
    "MIN(pt.artists) AS artists, "
    "MIN(pt.album_name) AS album_name, "
    "MIN(pt.added_at) AS added_at, "
    "MIN(pt.added_by) AS added_by, "
    "MIN(pt.position) AS position, "
    "MIN(pt.popularity) AS popularity "
    "FROM playlist_tracks AS pt "
    "LEFT JOIN audio_features_cache AS af ON af.track_uri = pt.track_uri "
    "WHERE af.track_uri IS NULL "
    "GROUP BY pt.track_uri "
    "ORDER BY pt.track_uri"
)


def load_uncached_tracks(conn: sqlite3.Connection) -> list[Track]:
    """Return one Track per distinct playlist track lacking a cache row."""
    rows = conn.execute(_QUERY).fetchall()
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
