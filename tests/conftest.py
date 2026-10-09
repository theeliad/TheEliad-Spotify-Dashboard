"""Shared pytest fixtures."""

import sqlite3
from collections.abc import Iterator
from pathlib import Path

import pytest

from src.db.db import get_db_connection
from src.schemas import Playlist, Track


@pytest.fixture
def tmp_db_path(tmp_path: Path) -> Path:
    return tmp_path / "test.db"


@pytest.fixture(autouse=True)
def _use_tmp_db(monkeypatch: pytest.MonkeyPatch, tmp_db_path: Path) -> None:
    monkeypatch.setenv("SPOTIFY_DB_PATH", str(tmp_db_path))


@pytest.fixture
def db_conn(tmp_db_path: Path) -> Iterator[sqlite3.Connection]:
    conn = get_db_connection(tmp_db_path)
    try:
        yield conn
    finally:
        conn.close()


@pytest.fixture
def sample_playlist() -> Playlist:
    return Playlist(
        playlist_id="playlist-1",
        name="Focus",
        owner_id="owner-1",
        collaborative=False,
        snapshot_id="snap-1",
        track_count=2,
    )


@pytest.fixture
def sample_tracks() -> list[Track]:
    return [
        Track(
            "spotify:track:a",
            "Alpha",
            "A Artist",
            "Album A",
            "2024-01-01T00:00:00Z",
            "owner-1",
            0,
        ),
        Track(
            "spotify:track:b",
            "Beta",
            "B Artist",
            "Album B",
            "2024-01-02T00:00:00Z",
            "owner-1",
            1,
        ),
    ]
