"""Tracks of a single selected playlist."""

import pandas as pd
import streamlit as st

from src.dashboard.utils.format import display_name_for
from src.db import load_app_users as app_users_db
from src.db import load_playlist_tracks as playlist_tracks_db


@st.cache_data(ttl=30)
def load_playlist_tracks(playlist_id: str) -> pd.DataFrame:
    """Read the current tracks of one playlist, with contributor names."""
    tracks = playlist_tracks_db.load_playlist_tracks(playlist_id)
    if tracks.empty:
        return tracks
    names = app_users_db.load_app_users()
    return tracks.assign(
        added_by=tracks["added_by"].map(lambda user_id: display_name_for(user_id, names))
    ).rename(columns={"added_by": "contributor"})


def render_playlist_detail(tracks: pd.DataFrame) -> None:
    """Draw the selected playlist's tracks."""
    st.subheader("Playlist tracks")
    if tracks.empty:
        st.info("No tracks for the selected playlist.")
        return
    st.dataframe(tracks, use_container_width=True, hide_index=True)
