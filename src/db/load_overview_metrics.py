"""Aggregate dashboard KPI counts from SQLite, optionally for one playlist."""

from src.db.db import db_connection
from src.schemas import OverviewMetrics


def load_overview_metrics(playlist_id: str | None = None) -> OverviewMetrics:
    """Return KPI counts for one playlist, or global aggregates when scoped out."""
    with db_connection() as conn:
        if playlist_id is None:
            playlist_count = conn.execute("SELECT COUNT(*) FROM playlists").fetchone()[0]
            track_count = conn.execute(
                "SELECT COUNT(DISTINCT track_uri) FROM playlist_tracks"
            ).fetchone()[0]
            events_24h = conn.execute(
                "SELECT COUNT(*) FROM track_events WHERE detected_at >= datetime('now', '-1 day')"
            ).fetchone()[0]
            last_polled_at = conn.execute("SELECT MAX(last_polled_at) FROM playlists").fetchone()[0]
        else:
            playlist_count = 1
            track_count = conn.execute(
                "SELECT COUNT(*) FROM playlist_tracks WHERE playlist_id = ?",
                (playlist_id,),
            ).fetchone()[0]
            events_24h = conn.execute(
                "SELECT COUNT(*) FROM track_events "
                "WHERE playlist_id = ? AND detected_at >= datetime('now', '-1 day')",
                (playlist_id,),
            ).fetchone()[0]
            last_polled_at = conn.execute(
                "SELECT last_polled_at FROM playlists WHERE playlist_id = ?",
                (playlist_id,),
            ).fetchone()[0]
    return OverviewMetrics(
        playlist_count=int(playlist_count),
        track_count=int(track_count),
        events_24h=int(events_24h),
        last_polled_at=last_polled_at,
    )
