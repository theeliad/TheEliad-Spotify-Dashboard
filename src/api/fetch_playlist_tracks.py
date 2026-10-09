"""Fetch the tracks of a single playlist."""

from spotipy import Spotify

from src.api.retry import call_with_backoff
from src.schemas import Track

_PAGE_SIZE = 100


def fetch_playlist_tracks(client: Spotify, playlist_id: str) -> list[Track]:
    """Return every track of a playlist in order.

    Uses the ``/items`` endpoint directly: spotipy 2.24.0 still requests the
    retired ``/tracks`` path, which the current API answers with HTTP 403.
    """
    tracks: list[Track] = []
    page = call_with_backoff(
        lambda: client._get(
            f"playlists/{playlist_id}/items",
            limit=_PAGE_SIZE,
            offset=0,
            additional_types="track",
        )
    )
    position = 0
    while page is not None:
        for item in page.get("items", []):
            track = Track.from_api(item, position)
            if track is not None:
                tracks.append(track)
            position += 1
        if not page.get("next"):
            break
        page = call_with_backoff(lambda page=page: client.next(page))
    return tracks
