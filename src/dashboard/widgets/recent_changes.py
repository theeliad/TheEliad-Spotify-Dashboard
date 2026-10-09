"""Recent change-event feed."""

import pandas as pd
import streamlit as st

from src.db import load_track_events as track_events_db

_COLUMNS = ["detected_at", "change_type", "track_name", "artists", "playlist_id"]


@st.cache_data(ttl=30)
def load_recent_changes(limit: int = 100) -> pd.DataFrame:
    """Read the newest change events from SQLite."""
    return track_events_db.load_track_events(limit=limit)


def render_recent_changes(events: pd.DataFrame) -> None:
    """Draw the recent-changes table."""
    st.subheader("Recent changes")
    if events.empty:
        st.info("No change events recorded yet.")
        return
    st.dataframe(events[_COLUMNS], use_container_width=True, hide_index=True)
