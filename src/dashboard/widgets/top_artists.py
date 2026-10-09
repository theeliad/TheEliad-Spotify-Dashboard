"""Most frequent artists across playlists."""

import pandas as pd
import plotly.express as px
import streamlit as st

from src.db import load_artist_counts as artist_counts_db


@st.cache_data(ttl=30)
def load_artist_counts(limit: int = 15) -> pd.DataFrame:
    """Read artist frequencies from SQLite."""
    return artist_counts_db.load_artist_counts(limit)


def render_top_artists(counts: pd.DataFrame) -> None:
    """Draw the top-artists chart."""
    st.subheader("Top artists")
    if counts.empty:
        st.info("No track data available yet.")
        return
    figure = px.bar(counts, x="track_count", y="artists", orientation="h")
    figure.update_layout(yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(figure, use_container_width=True)
