"""Fetch the authenticated user's own profile."""

from src.api.retry import call_with_backoff
from src.api.spotify_client import build_spotify_client
from src.schemas import CurrentUser
from src.settings import Settings


def fetch_current_user(settings: Settings) -> CurrentUser:
    """Return the authenticated user's profile using the cached token."""
    client = build_spotify_client(settings)
    payload = call_with_backoff(lambda: client.current_user())
    return CurrentUser.from_api(payload)
