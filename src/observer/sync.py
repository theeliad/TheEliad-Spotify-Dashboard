"""Run one observer poll cycle: fetch changes and persist them."""

import sqlite3
from datetime import UTC, datetime

from spotipy import Spotify

from src.api.fetch_playlist_tracks import fetch_playlist_tracks
from src.api.fetch_playlists import fetch_playlists
from src.api.spotify_client import build_spotify_client
from src.db.db import db_connection
from src.db.finish_poll_run import finish_poll_run
from src.db.load_playlist_snapshot import load_playlist_snapshot
from src.db.load_playlist_track_rows import load_playlist_track_rows
from src.db.load_tracked_playlists import load_tracked_playlist_ids
from src.db.write_playlist import write_playlist
from src.db.write_playlist_tracks import write_playlist_tracks
from src.db.write_poll_run import start_poll_run
from src.db.write_track_events import write_track_events
from src.observer.alerts import write_alert_payload
from src.observer.diff import diff_playlist_tracks
from src.schemas import Playlist, SyncResult
from src.settings import Settings


def _now() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")


def run_sync(settings: Settings) -> SyncResult:
    """Poll Spotify for changes, persist them, and return the outcome."""
    tracked_ids = set(load_tracked_playlist_ids())
    playlists_seen = 0
    events_added = 0
    error: str | None = None
    with db_connection(settings.db_path) as conn:
        run_id = start_poll_run(conn, _now())
        conn.commit()
        try:
            client = build_spotify_client(settings)
            for playlist in fetch_playlists(client):
                if playlist.playlist_id not in tracked_ids:
                    continue
                if load_playlist_snapshot(conn, playlist.playlist_id) != playlist.snapshot_id:
                    events_added += _record_change(conn, client, playlist, run_id)
                else:
                    write_playlist(conn, playlist, _now())
                conn.commit()
                playlists_seen += 1
        except Exception as exc:
            error = str(exc)
            conn.rollback()
        finally:
            finish_poll_run(conn, run_id, playlists_seen, events_added, error)
            conn.commit()
    return SyncResult(playlists_seen=playlists_seen, events_added=events_added, error=error)


def _record_change(
    conn: sqlite3.Connection, client: Spotify, playlist: Playlist, run_id: int
) -> int:
    """Diff, persist, and alert on a changed playlist, returning events written."""
    previous_tracks = load_playlist_track_rows(conn, playlist.playlist_id)
    current_tracks = fetch_playlist_tracks(client, playlist.playlist_id)
    events = diff_playlist_tracks(playlist.playlist_id, previous_tracks, current_tracks)
    write_playlist(conn, playlist, _now())
    write_playlist_tracks(conn, playlist.playlist_id, current_tracks)
    write_alert_payload(events, run_id)
    return write_track_events(conn, events)
