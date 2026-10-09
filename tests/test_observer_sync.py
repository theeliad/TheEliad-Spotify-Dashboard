"""Tests for the observer poll cycle."""

from pathlib import Path

from src.db.load_poll_runs import load_poll_runs
from src.db.load_track_events import load_track_events
from src.db.write_tracked_playlist import write_tracked_playlist
from src.observer import sync
from src.schemas import Playlist, Track
from src.settings import Settings


def _settings(db_path: Path) -> Settings:
    return Settings(
        client_id="client",
        client_secret="secret",
        redirect_uri="http://127.0.0.1/callback",
        db_path=db_path,
        cache_path=db_path.parent / ".cache",
    )


def _playlist(playlist_id: str, snapshot_id: str) -> Playlist:
    return Playlist(playlist_id, playlist_id, "owner", False, snapshot_id, 1)


def _track(uri: str, position: int = 0) -> Track:
    return Track(uri, uri, "artist", "album", None, None, position)


def _stub_api(monkeypatch, playlists: list[Playlist], tracks_by_playlist: dict) -> None:
    monkeypatch.setattr(sync, "build_spotify_client", lambda settings: object())
    monkeypatch.setattr(sync, "fetch_playlists", lambda client: playlists)
    monkeypatch.setattr(
        sync,
        "fetch_playlist_tracks",
        lambda client, playlist_id: tracks_by_playlist[playlist_id],
    )
    monkeypatch.setattr(sync, "write_alert_payload", lambda events, run_id: None)


def test_first_run_records_tracks_as_added(tmp_db_path, monkeypatch) -> None:
    write_tracked_playlist("p1")
    _stub_api(monkeypatch, [_playlist("p1", "snap-1")], {"p1": [_track("a"), _track("b", 1)]})
    result = sync.run_sync(_settings(tmp_db_path))
    assert result.playlists_seen == 1
    assert result.events_added == 2
    assert result.error is None
    assert len(load_track_events()) == 2


def test_unchanged_snapshot_skips_diff(tmp_db_path, monkeypatch) -> None:
    write_tracked_playlist("p1")
    _stub_api(monkeypatch, [_playlist("p1", "snap-1")], {"p1": [_track("a")]})
    sync.run_sync(_settings(tmp_db_path))
    _stub_api(monkeypatch, [_playlist("p1", "snap-1")], {"p1": [_track("a")]})
    result = sync.run_sync(_settings(tmp_db_path))
    assert result.events_added == 0
    assert len(load_track_events()) == 1


def test_changed_snapshot_records_delta(tmp_db_path, monkeypatch) -> None:
    write_tracked_playlist("p1")
    _stub_api(monkeypatch, [_playlist("p1", "snap-1")], {"p1": [_track("a")]})
    sync.run_sync(_settings(tmp_db_path))
    _stub_api(monkeypatch, [_playlist("p1", "snap-2")], {"p1": [_track("a"), _track("b", 1)]})
    result = sync.run_sync(_settings(tmp_db_path))
    assert result.events_added == 1
    assert len(load_track_events(playlist_id="p1")) == 2


def test_only_tracked_playlists_are_polled(tmp_db_path, monkeypatch) -> None:
    write_tracked_playlist("p1")
    _stub_api(
        monkeypatch,
        [_playlist("p1", "snap-1"), _playlist("p2", "snap-1")],
        {"p1": [_track("a")], "p2": [_track("b")]},
    )
    result = sync.run_sync(_settings(tmp_db_path))
    assert result.playlists_seen == 1
    assert len(load_track_events(playlist_id="p1")) == 1
    assert len(load_track_events(playlist_id="p2")) == 0


def test_api_failure_is_recorded(tmp_db_path, monkeypatch) -> None:
    monkeypatch.setattr(sync, "build_spotify_client", lambda settings: object())

    def boom(client) -> list[Playlist]:
        raise RuntimeError("api down")

    monkeypatch.setattr(sync, "fetch_playlists", boom)
    result = sync.run_sync(_settings(tmp_db_path))
    assert result.error == "api down"
    assert load_poll_runs().iloc[0]["error"] == "api down"
