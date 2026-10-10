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
    """Draw the selected playlist as a compact metric card."""
    st.subheader("Playlist")
    if selected.empty:
        st.info("Select a playlist to view its summary.")
        return
    row = selected.iloc[0]
    likes = int(row["likes"] or 0)
    tracks = int(row["tracks"] or 0)
    created = row["created"]
    last_polled = row["last_polled"]
    top = st.columns(2)
    top[0].metric("Owner", row["owner"])
    top[1].metric("Liked by", f"{likes:,}")
    bottom = st.columns(2)
    bottom[0].metric("Tracks", tracks)
    bottom[1].metric("Collaborative", row["collaborative"])
    st.caption(f"Created {created} · Last polled {last_polled}")
    st.link_button("Open in Spotify", row["url"])
