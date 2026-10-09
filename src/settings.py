"""Configuration loading. Reads .env and exposes typed settings."""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

SCOPES: tuple[str, ...] = (
    "playlist-read-private",
    "playlist-read-collaborative",
    "user-library-read",
    "user-read-recently-played",
)

PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent
DEFAULT_DB_PATH: Path = PROJECT_ROOT / "src" / "db" / "spotify.db"
DEFAULT_CACHE_PATH: Path = PROJECT_ROOT / ".cache"


class MissingCredentialsError(RuntimeError):
    """Raised when required Spotify credentials are absent from the environment."""


@dataclass(frozen=True)
class Settings:
    """Resolved runtime configuration."""

    client_id: str
    client_secret: str
    redirect_uri: str
    db_path: Path
    cache_path: Path


def _load_env() -> None:
    load_dotenv(PROJECT_ROOT / ".env")


def load_db_path() -> Path:
    """Resolve the SQLite path without requiring Spotify credentials."""
    _load_env()
    return Path(os.environ.get("SPOTIFY_DB_PATH", DEFAULT_DB_PATH))


def load_settings() -> Settings:
    """Load and validate settings from the environment."""
    _load_env()
    client_id = os.environ.get("SPOTIFY_CLIENT_ID", "")
    client_secret = os.environ.get("SPOTIFY_CLIENT_SECRET", "")
    redirect_uri = os.environ.get("SPOTIFY_REDIRECT_URI", "")
    if not client_id or not client_secret or not redirect_uri:
        raise MissingCredentialsError(
            "SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET and SPOTIFY_REDIRECT_URI must be set"
        )
    return Settings(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        db_path=Path(os.environ.get("SPOTIFY_DB_PATH", DEFAULT_DB_PATH)),
        cache_path=Path(os.environ.get("SPOTIFY_CACHE_PATH", DEFAULT_CACHE_PATH)),
    )
