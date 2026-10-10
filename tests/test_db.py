"""Tests for the SQLite persistence layer."""

from dataclasses import replace

import pytest

from src.db.finish_poll_run import finish_poll_run
from src.db.load_app_users import load_app_users
from src.db.load_artist_counts import load_artist_counts
from src.db.load_daily_change_counts import load_daily_change_counts
from src.db.load_overview_metrics import load_overview_metrics
from src.db.load_playlist_track_rows import load_playlist_track_rows
from src.db.load_playlist_tracks import load_playlist_tracks
from src.db.load_playlists import load_playlists
from src.db.load_poll_runs import load_poll_runs
from src.db.load_track_events import load_track_events
from src.db.load_tracked_playlists import load_tracked_playlist_ids
from src.db.write_app_user import write_app_user
from src.db.write_playlist import write_playlist
from src.db.write_playlist_tracks import write_playlist_tracks
from src.db.write_poll_run import start_poll_run
from src.db.write_track_events import write_track_events
from src.db.write_tracked_playlist import write_tracked_playlist
from src.schemas import Track, TrackEvent


def test_init_creates_tables(db_conn) -> None:
    rows = db_conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    names = {row[0] for row in rows}
    assert {
        "playlists",
        "playlist_tracks",
        "track_events",
        "poll_runs",
        "app_users",
        "play_events",
        "playlist_meta_snapshots",
    } <= names


def test_write_playlist_inserts_then_updates(db_conn, sample_playlist) -> None:
    write_playlist(db_conn, sample_playlist, "2024-01-01 00:00:00")
    db_conn.commit()
    updated = replace(sample_playlist, name="Renamed", snapshot_id="snap-2")
    write_playlist(db_conn, updated, "2024-01-02 00:00:00")
    db_conn.commit()

    playlists = load_playlists()
    assert len(playlists) == 1
    row = playlists.iloc[0]
    assert row["name"] == "Renamed"
    assert row["snapshot_id"] == "snap-2"
    assert row["first_seen_at"] == "2024-01-01 00:00:00"
    assert row["last_polled_at"] == "2024-01-02 00:00:00"


def test_write_playlist_tracks_is_wholesale(db_conn, sample_playlist, sample_tracks) -> None:
    write_playlist(db_conn, sample_playlist, "2024-01-01 00:00:00")
    write_playlist_tracks(db_conn, sample_playlist.playlist_id, sample_tracks)
    db_conn.commit()

    write_playlist_tracks(db_conn, sample_playlist.playlist_id, sample_tracks[:1])
    db_conn.commit()

    tracks = load_playlist_tracks(sample_playlist.playlist_id)
    assert len(tracks) == 1
    assert tracks.iloc[0]["track_uri"] == "spotify:track:a"


def test_write_playlist_tracks_collapses_duplicate_uri(db_conn, sample_playlist) -> None:
    write_playlist(db_conn, sample_playlist, "2024-01-01 00:00:00")
    first = Track("spotify:track:a", "Alpha", "A", "Album", None, None, 0)
    duplicate = Track("spotify:track:a", "Alpha duplicate", "A", "Album", None, None, 1)
    write_playlist_tracks(db_conn, sample_playlist.playlist_id, [first, duplicate])
    db_conn.commit()

    tracks = load_playlist_tracks(sample_playlist.playlist_id)
    assert len(tracks) == 1
    assert tracks.iloc[0]["track_name"] == "Alpha duplicate"


def test_write_track_events_appends_and_returns_count(db_conn) -> None:
    events = [
        TrackEvent("p1", "spotify:track:a", "Alpha", "A", None, None, "added"),
        TrackEvent("p1", "spotify:track:b", "Beta", "B", None, None, "removed"),
    ]
    assert write_track_events(db_conn, events) == 2
    db_conn.commit()

    frame = load_track_events(playlist_id="p1")
    assert len(frame) == 2
    assert set(frame["change_type"]) == {"added", "removed"}


def test_start_and_finish_poll_run(db_conn) -> None:
    run_id = start_poll_run(db_conn, "2024-01-01 00:00:00")
    finish_poll_run(db_conn, run_id, playlists_seen=3, events_added=5, error=None)
    db_conn.commit()

    runs = load_poll_runs()
    assert len(runs) == 1
    assert runs.iloc[0]["playlists_seen"] == 3
    assert runs.iloc[0]["events_added"] == 5
    assert runs.iloc[0]["finished_at"] is not None


def test_load_track_events_filters(db_conn) -> None:
    write_track_events(db_conn, [TrackEvent("p1", "u1", "n", "a", None, None, "added")])
    write_track_events(db_conn, [TrackEvent("p2", "u2", "n", "a", None, None, "added")])
    db_conn.commit()

    only_p1 = load_track_events(playlist_id="p1")
    assert len(only_p1) == 1
    assert only_p1.iloc[0]["playlist_id"] == "p1"

    limited = load_track_events(limit=1)
    assert len(limited) == 1


def test_load_daily_change_counts_filters_by_playlist(db_conn) -> None:
    write_track_events(db_conn, [TrackEvent("p1", "u1", "n", "a", None, None, "added")])
    write_track_events(db_conn, [TrackEvent("p2", "u2", "n", "a", None, None, "removed")])
    db_conn.commit()

    only_p1 = load_daily_change_counts(playlist_id="p1")
    assert len(only_p1) == 1
    assert only_p1.iloc[0]["change_type"] == "added"
    assert int(only_p1.iloc[0]["count"]) == 1


def test_write_tracked_playlist_is_idempotent() -> None:
    write_tracked_playlist("p1")
    write_tracked_playlist("p1")
    write_tracked_playlist("p2")
    assert load_tracked_playlist_ids() == ["p1", "p2"]


def test_write_app_user_upserts_display_name() -> None:
    write_app_user("u1", "Alice")
    write_app_user("u2", "Bob")
    assert load_app_users() == {"u1": "Alice", "u2": "Bob"}

    write_app_user("u1", "Alice Renamed")
    assert load_app_users()["u1"] == "Alice Renamed"


def test_load_artist_counts(db_conn, sample_playlist, sample_tracks) -> None:
    write_playlist(db_conn, sample_playlist, "2024-01-01 00:00:00")
    write_playlist_tracks(db_conn, sample_playlist.playlist_id, sample_tracks)
    db_conn.commit()

    counts = load_artist_counts()
    assert len(counts) == 2
    assert int(counts["track_count"].sum()) == 2

    scoped = load_artist_counts(playlist_id=sample_playlist.playlist_id)
    assert len(scoped) == 2

    out_of_scope = load_artist_counts(playlist_id="other-playlist")
    assert out_of_scope.empty


def test_load_overview_metrics(db_conn, sample_playlist, sample_tracks) -> None:
    write_playlist(db_conn, sample_playlist, "2024-01-01 00:00:00")
    write_playlist_tracks(db_conn, sample_playlist.playlist_id, sample_tracks)
    write_track_events(db_conn, [TrackEvent("p1", "u1", "n", "a", None, None, "added")])
    db_conn.commit()

    metrics = load_overview_metrics()
    assert metrics.playlist_count == 1
    assert metrics.track_count == 2
    assert metrics.events_24h == 1
    assert metrics.last_polled_at == "2024-01-01 00:00:00"

    scoped = load_overview_metrics(sample_playlist.playlist_id)
    assert scoped.playlist_count == 1
    assert scoped.track_count == 2
    assert scoped.events_24h == 1


def test_load_playlist_track_rows(db_conn, sample_playlist, sample_tracks) -> None:
    write_playlist(db_conn, sample_playlist, "2024-01-01 00:00:00")
    write_playlist_tracks(db_conn, sample_playlist.playlist_id, sample_tracks)
    db_conn.commit()

    rows = load_playlist_track_rows(db_conn, sample_playlist.playlist_id)
    assert [row.track_uri for row in rows] == ["spotify:track:a", "spotify:track:b"]


def test_interrupted_replace_rolls_back(db_conn, sample_playlist, sample_tracks) -> None:
    write_playlist(db_conn, sample_playlist, "2024-01-01 00:00:00")
    write_playlist_tracks(db_conn, sample_playlist.playlist_id, sample_tracks)
    db_conn.commit()

    with pytest.raises(AttributeError):
        write_playlist_tracks(db_conn, sample_playlist.playlist_id, [sample_tracks[0], None])
        db_conn.commit()
    db_conn.rollback()

    tracks = load_playlist_tracks(sample_playlist.playlist_id)
    assert len(tracks) == 2
