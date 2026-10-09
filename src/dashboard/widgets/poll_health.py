"""Poll-run health panel."""

import pandas as pd
import streamlit as st

from src.db import load_poll_runs as poll_runs_db


@st.cache_data(ttl=30)
def load_poll_runs(limit: int = 20) -> pd.DataFrame:
    """Read recent poll runs from SQLite."""
    return poll_runs_db.load_poll_runs(limit)


def render_poll_health(runs: pd.DataFrame) -> None:
    """Draw the poll-run health expander."""
    with st.expander("Poll health"):
        if runs.empty:
            st.info("No poll runs recorded yet.")
            return
        st.dataframe(runs, use_container_width=True, hide_index=True)
        errors = runs[runs["error"].notna()]
        if not errors.empty:
            st.error(f"{len(errors)} poll run(s) reported errors.")
