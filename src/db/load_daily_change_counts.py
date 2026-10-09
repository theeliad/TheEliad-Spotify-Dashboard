"""Aggregate add/remove event counts per day."""

import pandas as pd

from src.db.load_track_events import load_track_events


def load_daily_change_counts(playlist_id: str | None = None) -> pd.DataFrame:
    """Return add/remove counts grouped by detection day, optionally for one playlist."""
    events = load_track_events(playlist_id=playlist_id)
    if events.empty:
        return pd.DataFrame(columns=["day", "change_type", "count"])
    counted = events.copy()
    counted["day"] = pd.to_datetime(counted["detected_at"]).dt.date
    return counted.groupby(["day", "change_type"]).size().reset_index(name="count")
