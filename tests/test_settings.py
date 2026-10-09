"""Tests for settings loading."""

import pytest

from src.settings import SCOPES, MissingCredentialsError, load_settings


@pytest.fixture(autouse=True)
def _no_dotenv(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("src.settings.load_dotenv", lambda *args, **kwargs: None)


def _set_credentials(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SPOTIFY_CLIENT_ID", "client-id")
    monkeypatch.setenv("SPOTIFY_CLIENT_SECRET", "client-secret")
    monkeypatch.setenv("SPOTIFY_REDIRECT_URI", "http://127.0.0.1/callback")


def test_load_settings_reads_env(monkeypatch: pytest.MonkeyPatch) -> None:
    _set_credentials(monkeypatch)
    settings = load_settings()
    assert settings.client_id == "client-id"
    assert settings.client_secret == "client-secret"
    assert settings.redirect_uri == "http://127.0.0.1/callback"


def test_load_settings_default_paths(monkeypatch: pytest.MonkeyPatch) -> None:
    _set_credentials(monkeypatch)
    monkeypatch.delenv("SPOTIFY_DB_PATH", raising=False)
    monkeypatch.delenv("SPOTIFY_CACHE_PATH", raising=False)
    settings = load_settings()
    assert settings.db_path.name == "spotify.db"
    assert settings.cache_path.name == ".cache"


def test_load_settings_raises_without_credentials(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("SPOTIFY_CLIENT_ID", raising=False)
    monkeypatch.delenv("SPOTIFY_CLIENT_SECRET", raising=False)
    monkeypatch.delenv("SPOTIFY_REDIRECT_URI", raising=False)
    with pytest.raises(MissingCredentialsError):
        load_settings()


def test_scopes_exact_match() -> None:
    assert SCOPES == (
        "playlist-read-private",
        "playlist-read-collaborative",
        "user-library-read",
        "user-read-recently-played",
    )
