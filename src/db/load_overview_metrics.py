"""Aggregate dashboard KPI counts from SQLite."""

from src.db.db import db_connection
from src.schemas import OverviewMetrics


def load_overview_metrics() -> OverviewMetrics:
    """Return aggregate counts for the KPI row."""
    with db_connection() as conn:
        playlist_count = conn.execute("SELECT COUNT(*) FROM playlists").fetchone()[0]
        track_count = conn.execute(
            "SELECT COUNT(DISTINCT track_uri) FROM playlist_tracks"
        ).fetchone()[0]
        events_24h = conn.execute(
            "SELECT COUNT(*) FROM track_events WHERE detected_at >= datetime('now', '-1 day')"
        ).fetchone()[0]
        last_polled_at = conn.execute("SELECT MAX(last_polled_at) FROM playlists").fetchone()[0]
    return OverviewMetrics(
        playlist_count=int(playlist_count),
        track_count=int(track_count),
        events_24h=int(events_24h),
        last_polled_at=last_polled_at,
    )
