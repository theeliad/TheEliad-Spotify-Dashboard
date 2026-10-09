"""Streamlit dashboard wiring. Imports, layout, and interaction only."""

import pandas as pd
import streamlit as st

from src.dashboard.connect import render_connect
from src.dashboard.utils.format import spotify_playlist_url
from src.dashboard.widgets.additions_chart import load_daily_change_counts, render_additions_chart
from src.dashboard.widgets.overview_metrics import load_overview_metrics, render_overview_metrics
from src.dashboard.widgets.playlist_changes import load_playlist_changes, render_playlist_changes
from src.dashboard.widgets.playlist_contributors import (
    load_playlist_contributors,
    render_playlist_contributors,
)
from src.dashboard.widgets.playlist_detail import load_playlist_tracks, render_playlist_detail
from src.dashboard.widgets.playlist_table import load_playlists, render_playlist_table
from src.dashboard.widgets.playlist_timeline import load_playlist_timeline, render_playlist_timeline
from src.dashboard.widgets.poll_health import load_poll_runs, render_poll_health
from src.dashboard.widgets.recent_changes import load_recent_changes, render_recent_changes
from src.dashboard.widgets.top_artists import load_artist_counts, render_top_artists
from src.observer.sync import run_sync
from src.settings import MissingCredentialsError, load_settings

st.set_page_config(page_title="Spotify Playlist Dashboard", layout="wide")


def _run_sync() -> None:
    """Run one observer cycle, then drop caches so fresh data loads this run."""
    try:
        settings = load_settings()
    except MissingCredentialsError as exc:
        st.sidebar.error(str(exc))
        return
    with st.spinner("Syncing with Spotify..."):
        result = run_sync(settings)
    if result.error:
        st.sidebar.error(f"Sync failed: {result.error}")
    else:
        st.sidebar.success(
            f"Synced {result.playlists_seen} playlist(s); {result.events_added} new event(s)."
        )
    st.cache_data.clear()


def _render_sidebar_top() -> None:
    if st.sidebar.button("Sync now"):
        _run_sync()
    if st.sidebar.button("Refresh data"):
        st.cache_data.clear()
        st.rerun()
    st.sidebar.header("Connect Spotify")
    if render_connect():
        _run_sync()


def _render_sidebar_links(playlists: pd.DataFrame) -> None:
    st.sidebar.header("Playlists on Spotify")
    if playlists.empty:
        st.sidebar.caption("No playlists recorded yet.")
        return
    for playlist_id, name in zip(playlists["playlist_id"], playlists["name"], strict=True):
        st.sidebar.link_button(name, spotify_playlist_url(playlist_id))


def main() -> None:
    st.title("Spotify Playlist Dashboard")

    _render_sidebar_top()
    playlists = load_playlists()
    playlist_ids = [] if playlists.empty else playlists["playlist_id"].tolist()
    _render_sidebar_links(playlists)

    render_overview_metrics(load_overview_metrics())
    render_recent_changes(load_recent_changes())
    render_additions_chart(load_daily_change_counts())
    st.caption("Click a row to load its stats. Links open the playlist in Spotify.")
    selected_rows = render_playlist_table(playlists)
    if selected_rows:
        selected_playlist_id = playlist_ids[selected_rows[0]]
        render_playlist_detail(load_playlist_tracks(selected_playlist_id))
        render_playlist_contributors(load_playlist_contributors(selected_playlist_id))
        render_playlist_changes(load_playlist_changes(selected_playlist_id))
        render_playlist_timeline(load_playlist_timeline(selected_playlist_id))
    render_top_artists(load_artist_counts())
    render_poll_health(load_poll_runs())


main()
