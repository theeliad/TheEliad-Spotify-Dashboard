"""Fetch full metadata for a single playlist."""

from spotipy import Spotify

from src.api.retry import call_with_backoff
from src.schemas import PlaylistMeta


def fetch_playlist_detail(client: Spotify, playlist_id: str) -> PlaylistMeta:
    """Return full playlist metadata: owner name and follower count included."""
    payload = call_with_backoff(lambda: client.playlist(playlist_id))
    return PlaylistMeta.from_api(payload)
