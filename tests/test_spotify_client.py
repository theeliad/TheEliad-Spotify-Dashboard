"""Tests for Spotify client construction."""

from pathlib import Path

import pytest

from src.api import spotify_client
from src.settings import Settings


def test_build_spotify_client_configures_oauth(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    captured: dict = {}

    def fake_oauth(**kwargs):
        captured.update(kwargs)
        return "auth-manager"

    def fake_spotify(auth_manager):
        captured["auth_manager"] = auth_manager
        return "spotify-client"

    monkeypatch.setattr(spotify_client, "SpotifyOAuth", fake_oauth)
    monkeypatch.setattr(spotify_client, "Spotify", fake_spotify)
    settings = Settings(
        client_id="client",
        client_secret="secret",
        redirect_uri="http://127.0.0.1/callback",
        db_path=tmp_path / "db.sqlite",
        cache_path=tmp_path / ".cache",
    )
    client = spotify_client.build_spotify_client(settings)
    assert client == "spotify-client"
    assert captured["auth_manager"] == "auth-manager"
    assert captured["scope"] == (
        "playlist-read-private playlist-read-collaborative "
        "user-library-read user-read-recently-played"
    )
    assert captured["open_browser"] is True
    assert (tmp_path / ".cache").is_dir()
