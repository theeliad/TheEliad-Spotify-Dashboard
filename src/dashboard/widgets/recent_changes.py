"""Recent change-event feed for one playlist."""

import pandas as pd
import streamlit as st

from src.db import load_track_events as track_events_db

_COLUMNS = ["change_type", "track_name", "artists", "added_at", "detected_at"]


@st.cache_data(ttl=30)
def load_recent_changes(playlist_id: str, limit: int = 100) -> pd.DataFrame:
    """Read the newest change events for one playlist from SQLite."""
    return track_events_db.load_track_events(playlist_id=playlist_id, limit=limit)


def render_recent_changes(events: pd.DataFrame) -> None:
    """Draw the recent-changes table with Spotify's true added date."""
    st.subheader("Recent changes")
    if events.empty:
        st.info("No change events recorded for this playlist yet.")
        return
    st.dataframe(
        events[_COLUMNS],
        use_container_width=True,
        hide_index=True,
        column_config={
            "change_type": "Type",
            "track_name": "Track",
            "added_at": "When added (Spotify)",
            "detected_at": "Detected (poll)",
        },
    )