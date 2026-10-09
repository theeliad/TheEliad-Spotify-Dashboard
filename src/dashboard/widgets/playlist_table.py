"""Playlist summary table."""

import pandas as pd
import streamlit as st

from src.dashboard.utils.format import spotify_playlist_url
from src.db import load_playlists as playlists_db


@st.cache_data(ttl=30)
def load_playlists() -> pd.DataFrame:
    """Read all playlists from SQLite."""
    return playlists_db.load_playlists()


def render_playlist_table(playlists: pd.DataFrame) -> list[int]:
    """Draw the playlist table and return the selected row positions."""
    st.subheader("Playlists")
    if playlists.empty:
        st.info("No playlists recorded yet. Run the observer to populate the database.")
        return []
    display = playlists.assign(url=playlists["playlist_id"].map(spotify_playlist_url))
    event = st.dataframe(
        display,
        use_container_width=True,
        hide_index=True,
        column_config={"url": st.column_config.LinkColumn("Spotify", display_text="Open")},
        on_select="rerun",
        selection_mode="single-row",
        key="playlist_table",
    )
    return event["selection"]["rows"]
