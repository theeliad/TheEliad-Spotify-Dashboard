"""Change-event feed for a single playlist."""

import pandas as pd
import streamlit as st

from src.dashboard.utils.format import display_name_for
from src.db import load_app_users as app_users_db
from src.db import load_track_events as track_events_db

_COLUMNS = ["detected_at", "change_type", "track_name", "artists", "added_at", "contributor"]


@st.cache_data(ttl=30)
def load_playlist_changes(playlist_id: str, limit: int = 100) -> pd.DataFrame:
    """Read the newest change events of one playlist, with contributor names."""
    events = track_events_db.load_track_events(playlist_id=playlist_id, limit=limit)
    if events.empty:
        return events
    names = app_users_db.load_app_users()
    events = events.assign(
        contributor=events["added_by"].map(lambda user_id: display_name_for(user_id, names))
    )
    return events[_COLUMNS]


def render_playlist_changes(events: pd.DataFrame) -> None:
    """Draw the selected playlist's change events."""
    st.subheader("Playlist changes")
    if events.empty:
        st.info("No change events recorded for this playlist.")
        return
    st.dataframe(events[_COLUMNS], use_container_width=True, hide_index=True)
