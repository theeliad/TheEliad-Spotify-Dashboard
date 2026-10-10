"""Most-played panel for the selected playlist."""

import pandas as pd
import streamlit as st

from src.db import load_playlist_plays as playlist_plays_db


@st.cache_data(ttl=30)
def load_playlist_plays(playlist_id: str) -> pd.DataFrame:
    """Read the selected playlist's tracks with play counts and popularity."""
    return playlist_plays_db.load_playlist_plays(playlist_id)


def _render_played_ranked(counts: pd.DataFrame) -> None:
    played = counts[counts["play_count"] > 0].sort_values(
        "play_count", ascending=False
    )
    if played.empty:
        st.info("No play activity recorded for this playlist yet. Sync to start tracking.")
        return
    st.dataframe(
        played[["track_name", "artists", "play_count"]],
        use_container_width=True,
        hide_index=True,
        column_config={
            "track_name": "Track",
            "play_count": st.column_config.NumberColumn("Times played by you"),
        },
    )


def _render_popularity_ranked(counts: pd.DataFrame) -> None:
    ranked = counts[counts["popularity"].notna()].sort_values(
        "popularity", ascending=False
    )
    if ranked.empty:
        st.caption("No popularity data for this playlist yet.")
        return
    top = ranked.head(15)
    st.dataframe(
        top[["track_name", "artists", "popularity"]],
        use_container_width=True,
        hide_index=True,
        column_config={
            "track_name": "Track",
            "popularity": st.column_config.NumberColumn("Popularity (0-100)"),
        },
    )


def render_playlist_plays(counts: pd.DataFrame) -> None:
    """Draw the selected playlist's most-played tracks and top popularity."""
    st.subheader("Most played")
    if counts.empty:
        st.info("No track data for the selected playlist yet.")
        return
    st.caption("Play counts measure your own listens since tracking began.")
    _render_played_ranked(counts)
    st.markdown("**Highest Spotify popularity**")
    _render_popularity_ranked(counts)