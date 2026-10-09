"""Tests for playlist and playlist-track fetching."""

from src.api.fetch_playlist_tracks import fetch_playlist_tracks
from src.api.fetch_playlists import fetch_playlists


class _FakeClient:
    def __init__(self, pages: list[dict]) -> None:
        self._pages = pages
        self._index = 0

    def current_user_playlists(self, limit: int) -> dict:
        return self._pages[0]

    def _get(self, url: str, **kwargs) -> dict:
        return self._pages[0]

    def next(self, page: dict) -> dict:
        self._index += 1
        return self._pages[self._index]


def _playlist_payload(playlist_id: str) -> dict:
    return {
        "id": playlist_id,
        "name": playlist_id,
        "owner": {"id": "owner"},
        "collaborative": False,
        "snapshot_id": "snap",
        "items": {"total": 1},
    }


def _track_item(uri: str, *, key: str = "item") -> dict:
    return {
        key: {
            "uri": uri,
            "name": uri,
            "artists": [{"name": "A"}],
            "album": {"name": "Al"},
        },
        "added_at": None,
        "added_by": None,
    }


def test_fetch_playlists_follows_pagination() -> None:
    pages = [
        {"items": [_playlist_payload("p1"), _playlist_payload("p2")], "next": "url"},
        {"items": [_playlist_payload("p3")], "next": None},
    ]
    result = fetch_playlists(_FakeClient(pages))
    assert [playlist.playlist_id for playlist in result] == ["p1", "p2", "p3"]
    assert [playlist.track_count for playlist in result] == [1, 1, 1]


def test_fetch_playlist_tracks_follows_pagination() -> None:
    pages = [
        {"items": [_track_item("spotify:track:a")], "next": "url"},
        {"items": [_track_item("spotify:track:b")], "next": None},
    ]
    tracks = fetch_playlist_tracks(_FakeClient(pages), "p1")
    assert [track.track_uri for track in tracks] == ["spotify:track:a", "spotify:track:b"]
    assert [track.position for track in tracks] == [0, 1]


def test_fetch_playlist_tracks_accepts_legacy_track_key() -> None:
    pages = [{"items": [_track_item("spotify:track:c", key="track")], "next": None}]
    tracks = fetch_playlist_tracks(_FakeClient(pages), "p1")
    assert [track.track_uri for track in tracks] == ["spotify:track:c"]
