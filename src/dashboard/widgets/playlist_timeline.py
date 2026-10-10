"""Daily adds/removals chart for a single playlist."""

import pandas as pd
import plotly.express as px
import streamlit as st

from src.db import load_daily_change_counts as daily_changes_db


@st.cache_data(ttl=30)
def load_playlist_timeline(playlist_id: str) -> pd.DataFrame:
    """Read one playlist's per-day add/remove counts."""
    return daily_changes_db.load_daily_change_counts(playlist_id=playlist_id)


def render_playlist_timeline(counts: pd.DataFrame) -> None:
    """Draw the selected playlist's adds/removals-per-day chart."""
    st.subheader("Playlist adds and removals per day")
    st.caption("Adds by Spotify's added date; removals by the date they were detected.")
    if counts.empty:
        st.info("Not enough history to chart yet.")
        return
    figure = px.bar(counts, x="day", y="count", color="change_type", barmode="group")
    st.plotly_chart(figure, use_container_width=True)
