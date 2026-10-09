"""Fetch the current user's playlists."""

from spotipy import Spotify

from src.api.retry import call_with_backoff
from src.api.spotify_client import build_spotify_client
from src.schemas import Playlist
from src.settings import Settings

_PAGE_SIZE = 50


def fetch_all_playlists(settings: Settings) -> list[Playlist]:
    """Authenticate with the cached token and return every visible playlist."""
    return fetch_playlists(build_spotify_client(settings))


def fetch_playlists(client: Spotify) -> list[Playlist]:
    """Return every playlist visible to the authenticated user."""
    playlists: list[Playlist] = []
    page = call_with_backoff(lambda: client.current_user_playlists(limit=_PAGE_SIZE))
    while page is not None:
        playlists.extend(Playlist.from_api(item) for item in page.get("items", []))
        if not page.get("next"):
            break
        page = call_with_backoff(lambda page=page: client.next(page))
    return playlists
