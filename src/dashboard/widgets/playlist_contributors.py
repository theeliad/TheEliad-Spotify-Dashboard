"""Per-contributor history for a single playlist."""

import pandas as pd
import streamlit as st

from src.dashboard.utils.format import display_name_for
from src.db import load_app_users as app_users_db
from src.db import load_playlist_tracks as playlist_tracks_db

_COLUMNS = ["contributor", "tracks", "first_added", "last_added"]


@st.cache_data(ttl=30)
def load_playlist_contributors(playlist_id: str) -> pd.DataFrame:
    """Aggregate a playlist's current tracks by the user who added them."""
    tracks = playlist_tracks_db.load_playlist_tracks(playlist_id)
    if tracks.empty:
        return pd.DataFrame(columns=_COLUMNS)
    names = app_users_db.load_app_users()
    contributors = tracks.assign(
        contributor=tracks["added_by"].map(lambda user_id: display_name_for(user_id, names))
    )
    grouped = contributors.groupby("contributor", as_index=False).agg(
        tracks=("track_uri", "count"),
        first_added=("added_at", "min"),
        last_added=("added_at", "max"),
    )
    return grouped.sort_values("tracks", ascending=False)[_COLUMNS]


def render_playlist_contributors(contributors: pd.DataFrame) -> None:
    """Draw the selected playlist's per-contributor summary."""
    st.subheader("Contributors")
    if contributors.empty:
        st.info("No contributor data for the selected playlist.")
        return
    st.dataframe(contributors, use_container_width=True, hide_index=True)
