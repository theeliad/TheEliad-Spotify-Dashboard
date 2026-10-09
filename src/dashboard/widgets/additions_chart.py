"""Daily adds/removals bar chart."""

import pandas as pd
import plotly.express as px
import streamlit as st

from src.db import load_daily_change_counts as daily_changes_db


@st.cache_data(ttl=30)
def load_daily_change_counts() -> pd.DataFrame:
    """Read per-day add/remove counts from SQLite."""
    return daily_changes_db.load_daily_change_counts()


def render_additions_chart(counts: pd.DataFrame) -> None:
    """Draw the adds/removals-per-day chart."""
    st.subheader("Adds and removals per day")
    if counts.empty:
        st.info("Not enough history to chart yet.")
        return
    figure = px.bar(counts, x="day", y="count", color="change_type", barmode="group")
    st.plotly_chart(figure, use_container_width=True)
