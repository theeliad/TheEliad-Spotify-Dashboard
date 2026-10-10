"""Scope-style BPM ribbon for a single playlist."""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.graph_objects import Figure

from src.db import load_playlist_tempo as playlist_tempo_db


@st.cache_data(ttl=30)
def load_playlist_tempo(playlist_id: str) -> pd.DataFrame:
    """Read one playlist's tracks with cached tempo and duration."""
    return playlist_tempo_db.load_playlist_tempo(playlist_id)


def _bpm_figure(tempo: pd.DataFrame) -> Figure:
    """Build a mirrored scope-style ribbon of BPM across playlist positions."""
    positions = tempo["position"]
    bpm = tempo["tempo"]
    labels = list(
        zip(
            tempo["track_name"].fillna("").tolist(),
            tempo["artists"].fillna("").tolist(),
            strict=True,
        )
    )
    figure = Figure()
    figure.add_trace(
        go.Scatter(
            x=positions,
            y=bpm,
            mode="lines",
            line={"color": "#1DB954", "width": 1.5},
            connectgaps=False,
            fill="tozeroy",
            fillcolor="rgba(29, 185, 84, 0.25)",
            customdata=labels,
            hovertemplate=("BPM %{y:.1f}<br>%{customdata[0]} — %{customdata[1]}<extra></extra>"),
        )
    )
    figure.add_trace(
        go.Scatter(
            x=positions,
            y=-bpm,
            mode="lines",
            line={"color": "#1DB954", "width": 1.5},
            connectgaps=False,
            fill="tozeroy",
            fillcolor="rgba(29, 185, 84, 0.25)",
            hoverinfo="skip",
        )
    )
    figure.add_hline(y=0, line_dash="dot", line_color="rgba(255, 255, 255, 0.25)")
    figure.update_layout(
        xaxis_title="Track position",
        yaxis_title="BPM",
        showlegend=False,
        margin={"t": 8, "b": 8, "l": 8, "r": 8},
    )
    return figure


def render_playlist_bpm(tempo: pd.DataFrame) -> None:
    """Draw the selected playlist's BPM scope; gaps where data is missing."""
    st.subheader("Playlist BPM oscillogram")
    available = int(tempo["tempo"].notna().sum())
    if available == 0:
        st.info("No tempo data for this playlist yet. Run `python -m src.tempo` to backfill.")
        return
    st.caption(f"{available} of {len(tempo)} tracks have tempo data.")
    st.plotly_chart(_bpm_figure(tempo), use_container_width=True)
