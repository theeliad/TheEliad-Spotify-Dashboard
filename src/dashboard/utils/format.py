"""Pure display helpers for the dashboard."""

from collections.abc import Mapping
from datetime import datetime


def spotify_playlist_url(playlist_id: str) -> str:
    """Build the public Spotify URL for a playlist."""
    return f"https://open.spotify.com/playlist/{playlist_id}"


def display_name_for(user_id: str | None, names: Mapping[str, str]) -> str:
    """Return a contributor's name, falling back to the raw user id."""
    if not user_id:
        return "unknown"
    return names.get(user_id, user_id)


def format_duration(milliseconds: int) -> str:
    """Render milliseconds as m:ss."""
    total_seconds = max(0, milliseconds // 1000)
    minutes, seconds = divmod(total_seconds, 60)
    return f"{minutes}:{seconds:02d}"


def format_timestamp(iso_value: str) -> str:
    """Render a SQLite timestamp in a compact, human-readable form."""
    if not iso_value:
        return ""
    try:
        parsed = datetime.fromisoformat(iso_value)
    except ValueError:
        return iso_value
    return parsed.strftime("%Y-%m-%d %H:%M")
