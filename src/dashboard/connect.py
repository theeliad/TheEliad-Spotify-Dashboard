"""Sanctioned in-app OAuth flow: log in and choose playlists to track."""

import streamlit as st

from src.api.fetch_current_user import fetch_current_user
from src.api.fetch_playlists import fetch_all_playlists
from src.api.spotify_client import (
    exchange_code_for_token,
    get_authorize_url,
    has_cached_token,
)
from src.db.load_tracked_playlists import load_tracked_playlist_ids
from src.db.write_app_user import write_app_user
from src.db.write_tracked_playlist import write_tracked_playlist
from src.schemas import CurrentUser, Playlist
from src.settings import MissingCredentialsError, Settings, load_settings


def _load_settings() -> Settings | None:
    try:
        return load_settings()
    except MissingCredentialsError as exc:
        st.sidebar.error(str(exc))
        return None


@st.cache_data(ttl=300)
def _load_user_playlists(settings: Settings) -> list[Playlist]:
    """Fetch the playlists the authenticated user owns or follows."""
    return fetch_all_playlists(settings)


@st.cache_data(ttl=30)
def _load_tracked_ids() -> list[str]:
    """Read the currently tracked playlist ids."""
    return load_tracked_playlist_ids()


@st.cache_data(ttl=3600)
def _load_current_user(settings: Settings) -> CurrentUser:
    """Fetch the authenticated user's own profile."""
    return fetch_current_user(settings)


def _render_picker(settings: Settings) -> bool:
    playlists = _load_user_playlists(settings)
    names_by_id = {playlist.playlist_id: playlist.name for playlist in playlists}
    tracked = set(_load_tracked_ids())
    selected = st.sidebar.multiselect(
        "Playlists to track",
        options=list(names_by_id),
        default=[playlist_id for playlist_id in names_by_id if playlist_id in tracked],
        format_func=lambda playlist_id: names_by_id[playlist_id],
    )
    if st.sidebar.button("Save tracked playlists"):
        for playlist_id in selected:
            write_tracked_playlist(playlist_id)
        st.sidebar.success(f"Tracking {len(selected)} playlist(s).")
        return True
    return False


def render_connect() -> bool:
    """Run the OAuth login if needed, then let the user pick playlists to track.

    Returns True when the user just saved their tracked playlists.
    """
    settings = _load_settings()
    if settings is None:
        return False
    if code := st.query_params.get("code"):
        exchange_code_for_token(settings, code)
        st.query_params.clear()
        st.rerun()
    if not has_cached_token(settings):
        st.sidebar.link_button("Log in with Spotify", get_authorize_url(settings))
        return False
    current_user = _load_current_user(settings)
    write_app_user(current_user.user_id, current_user.display_name)
    return _render_picker(settings)
