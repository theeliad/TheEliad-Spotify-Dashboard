"""Aggregate add/remove event counts per day."""

import pandas as pd

from src.db.load_track_events import load_track_events


def load_daily_change_counts(playlist_id: str | None = None) -> pd.DataFrame:
    """Return add/remove counts grouped by day, optionally for one playlist.

    Adds are grouped by Spotify's ``added_at`` when present (falling back to the
    detection time), because Spotify has no removal timestamps removals are
    always grouped by ``detected_at``.
    """
    events = load_track_events(playlist_id=playlist_id)
    if events.empty:
        return pd.DataFrame(columns=["day", "change_type", "count"])
    counted = events.copy()
    is_added = counted["change_type"] == "added"
    counted["day"] = counted["added_at"].where(is_added).fillna(counted["detected_at"])
    counted["day"] = pd.to_datetime(counted["day"]).dt.date
    return counted.groupby(["day", "change_type"]).size().reset_index(name="count")
