"""Fetch the authenticated user's recently played tracks."""

from spotipy import Spotify

from src.api.retry import call_with_backoff
from src.schemas import PlayEvent


def fetch_recently_played(client: Spotify, limit: int = 50) -> list[PlayEvent]:
    """Return up to ``limit`` of the user's most recent plays, oldest first."""
    page = call_with_backoff(lambda: client.current_user_recently_played(limit=limit))
    events: list[PlayEvent] = []
    for item in (page.get("items") or []) if isinstance(page, dict) else []:
        event = PlayEvent.from_api(item)
        if event is not None:
            events.append(event)
    return events