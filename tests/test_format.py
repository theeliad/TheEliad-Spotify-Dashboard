"""Tests for dashboard display helpers."""

from src.dashboard.utils.format import display_name_for, spotify_playlist_url


def test_spotify_playlist_url() -> None:
    assert spotify_playlist_url("abc123") == "https://open.spotify.com/playlist/abc123"


def test_display_name_for_resolves_known_user() -> None:
    assert display_name_for("u1", {"u1": "Alice"}) == "Alice"


def test_display_name_for_falls_back_to_id() -> None:
    assert display_name_for("u2", {"u1": "Alice"}) == "u2"


def test_display_name_for_handles_missing_id() -> None:
    assert display_name_for(None, {}) == "unknown"
