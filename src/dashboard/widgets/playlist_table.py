"""Selected-playlist summary table."""

import pandas as pd
import streamlit as st

from src.dashboard.utils.format import spotify_playlist_url
from src.db import load_playlist_meta as playlist_meta_db
from src.db import load_playlist_tracks as playlist_tracks_db
from src.db import load_playlists as playlists_db


@st.cache_data(ttl=30)
def load_playlists() -> pd.DataFrame:
    """Read all playlists from SQLite."""
    return playlists_db.load_playlists()


@st.cache_data(ttl=30)
def load_selected_playlist(playlist_id: str) -> pd.DataFrame:
    """Return a one-row summary for the selected playlist, or an empty frame."""
    base = playlists_db.load_playlists()
    matches = base[base["playlist_id"] == playlist_id]
    if matches.empty:
        return pd.DataFrame()
    row = matches.iloc[0]
    meta = playlist_meta_db.load_playlist_meta(playlist_id) or {}
    created = playlist_tracks_db.earliest_added_at(playlist_id) or "—"
    owner = meta.get("owner_display_name") or row["owner_id"]
    owner = owner if isinstance(owner, str) and owner else "—"
    return pd.DataFrame(
        [
            {
                "name": row["name"],
                "owner": owner,
                "likes": meta.get("follower_count", 0),
                "created": created,
                "tracks": int(row["track_count"]),
                "collaborative": "yes" if bool(row["collaborative"]) else "no",
                "last_polled": row["last_polled_at"],
                "url": spotify_playlist_url(playlist_id),
            }
        ]
    )


def render_playlist_table(selected: pd.DataFrame) -> None:
    """Draw the selected playlist's summary row (no row selection)."""
    st.subheader("Playlist")
    if selected.empty:
        st.info("Select a playlist to view its summary.")
        return
    st.dataframe(
        selected,
        use_container_width=True,
        hide_index=True,
        column_config={
            "likes": st.column_config.NumberColumn("Liked by"),
            "created": "Created (approx.)",
            "collaborative": "Collaborative",
            "last_polled": "Last polled",
            "url": st.column_config.LinkColumn("Spotify", display_text="Open"),
        },
    )