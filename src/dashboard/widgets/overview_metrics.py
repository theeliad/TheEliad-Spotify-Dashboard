"""Overview KPI metrics."""

import streamlit as st

from src.db import load_overview_metrics as overview_metrics_db
from src.schemas import OverviewMetrics


@st.cache_data(ttl=30)
def load_overview_metrics() -> OverviewMetrics:
    """Read aggregate counts from SQLite."""
    return overview_metrics_db.load_overview_metrics()


def render_overview_metrics(metrics: OverviewMetrics) -> None:
    """Draw the KPI row."""
    columns = st.columns(4)
    columns[0].metric("Playlists", metrics.playlist_count)
    columns[1].metric("Distinct tracks", metrics.track_count)
    columns[2].metric("Changes (24h)", metrics.events_24h)
    columns[3].metric("Last poll", metrics.last_polled_at or "never")
