"""Tests for playlist snapshot diffing."""

from src.observer.diff import diff_playlist_tracks
from src.schemas import Track


def _track(uri: str, position: int = 0) -> Track:
    return Track(uri, uri, "artist", "album", None, None, position)


def test_detects_added_and_removed() -> None:
    previous = [_track("spotify:track:a"), _track("spotify:track:b", 1)]
    current = [_track("spotify:track:b"), _track("spotify:track:c", 1)]
    events = diff_playlist_tracks("p1", previous, current)
    added = {event.track_uri for event in events if event.change_type == "added"}
    removed = {event.track_uri for event in events if event.change_type == "removed"}
    assert added == {"spotify:track:c"}
    assert removed == {"spotify:track:a"}


def test_identical_membership_yields_no_events() -> None:
    tracks = [_track("spotify:track:a")]
    assert diff_playlist_tracks("p1", tracks, tracks) == []
