"""Compute added and removed events between two playlist snapshots."""

from collections.abc import Sequence

from src.schemas import ChangeType, Track, TrackEvent


def diff_playlist_tracks(
    playlist_id: str, previous: Sequence[Track], current: Sequence[Track]
) -> list[TrackEvent]:
    """Return added and removed events from previous to current membership."""
    previous_uris = {track.track_uri for track in previous}
    current_uris = {track.track_uri for track in current}
    added = [
        _event(playlist_id, track, "added")
        for track in current
        if track.track_uri not in previous_uris
    ]
    removed = [
        _event(playlist_id, track, "removed")
        for track in previous
        if track.track_uri not in current_uris
    ]
    return added + removed


def _event(playlist_id: str, track: Track, change_type: ChangeType) -> TrackEvent:
    return TrackEvent(
        playlist_id=playlist_id,
        track_uri=track.track_uri,
        track_name=track.track_name,
        artists=track.artists,
        added_at=track.added_at,
        added_by=track.added_by,
        change_type=change_type,
    )
