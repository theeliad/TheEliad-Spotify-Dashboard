"""Serializable data shapes shared across the application."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Literal

ChangeType = Literal["added", "removed"]


def _text(value: Any) -> str:
    return value if isinstance(value, str) else ""


def _parse_artists(track: Mapping[str, Any]) -> str:
    artists = track.get("artists") or []
    names = [a.get("name", "") for a in artists if isinstance(a, Mapping)]
    return ", ".join(name for name in names if name)


@dataclass(frozen=True)
class Playlist:
    """A playlist and its last-seen snapshot."""

    playlist_id: str
    name: str
    owner_id: str | None
    collaborative: bool
    snapshot_id: str
    track_count: int

    @classmethod
    def from_api(cls, payload: Mapping[str, Any]) -> Playlist:
        owner = payload.get("owner")
        tracks = payload.get("items") or payload.get("tracks")
        return cls(
            playlist_id=_text(payload.get("id")),
            name=_text(payload.get("name")),
            owner_id=owner.get("id") if isinstance(owner, Mapping) else None,
            collaborative=bool(payload.get("collaborative")),
            snapshot_id=_text(payload.get("snapshot_id")),
            track_count=int(tracks.get("total") or 0) if isinstance(tracks, Mapping) else 0,
        )


@dataclass(frozen=True)
class Track:
    """One track as observed inside a playlist."""

    track_uri: str
    track_name: str
    artists: str
    album_name: str
    added_at: str | None
    added_by: str | None
    position: int
    popularity: int | None = None

    @classmethod
    def from_api(cls, item: Mapping[str, Any], position: int) -> Track | None:
        track = item.get("item") or item.get("track")
        if not isinstance(track, Mapping) or not track.get("uri"):
            return None
        album = track.get("album")
        added_by = item.get("added_by")
        popularity = track.get("popularity")
        return cls(
            track_uri=_text(track.get("uri")),
            track_name=_text(track.get("name")),
            artists=_parse_artists(track),
            album_name=_text(album.get("name")) if isinstance(album, Mapping) else "",
            added_at=item.get("added_at") if isinstance(item.get("added_at"), str) else None,
            added_by=added_by.get("id") if isinstance(added_by, Mapping) else None,
            position=position,
            popularity=popularity if isinstance(popularity, int) else None,
        )


@dataclass(frozen=True)
class AudioFeature:
    """Cached tempo and duration for one track."""

    track_uri: str
    tempo: float | None
    duration_ms: int | None


@dataclass(frozen=True)
class Preview:
    """A 30-second audio preview resolved from a third-party provider."""

    url: str
    duration_ms: int | None


@dataclass(frozen=True)
class PlaylistMeta:
    """Full playlist metadata used for follower and owner display."""

    playlist_id: str
    name: str
    owner_id: str | None
    owner_display_name: str | None
    follower_count: int
    collaborative: bool
    snapshot_id: str

    @classmethod
    def from_api(cls, payload: Mapping[str, Any]) -> PlaylistMeta:
        owner = payload.get("owner")
        followers = payload.get("followers")
        return cls(
            playlist_id=_text(payload.get("id")),
            name=_text(payload.get("name")),
            owner_id=owner.get("id") if isinstance(owner, Mapping) else None,
            owner_display_name=(
                owner.get("display_name") if isinstance(owner, Mapping) else None
            ),
            follower_count=(
                int(followers.get("total") or 0) if isinstance(followers, Mapping) else 0
            ),
            collaborative=bool(payload.get("collaborative")),
            snapshot_id=_text(payload.get("snapshot_id")),
        )


@dataclass(frozen=True)
class SavedTrack:
    """One track saved to the user's library."""

    track_uri: str
    track_name: str
    artists: str
    album_name: str
    added_at: str | None

    @classmethod
    def from_api(cls, item: Mapping[str, Any]) -> SavedTrack | None:
        track = item.get("track")
        if not isinstance(track, Mapping) or not track.get("uri"):
            return None
        album = track.get("album")
        return cls(
            track_uri=_text(track.get("uri")),
            track_name=_text(track.get("name")),
            artists=_parse_artists(track),
            album_name=_text(album.get("name")) if isinstance(album, Mapping) else "",
            added_at=item.get("added_at") if isinstance(item.get("added_at"), str) else None,
        )


@dataclass(frozen=True)
class PlayEvent:
    """One recently-played event."""

    track_uri: str
    track_name: str
    artists: str
    played_at: str

    @classmethod
    def from_api(cls, item: Mapping[str, Any]) -> PlayEvent | None:
        track = item.get("track")
        played_at = item.get("played_at")
        if not isinstance(track, Mapping) or not track.get("uri"):
            return None
        if not isinstance(played_at, str) or not played_at:
            return None
        return cls(
            track_uri=_text(track.get("uri")),
            track_name=_text(track.get("name")),
            artists=_parse_artists(track),
            played_at=played_at,
        )


@dataclass(frozen=True)
class TrackEvent:
    """An immutable playlist change event."""

    playlist_id: str
    track_uri: str
    track_name: str
    artists: str
    added_at: str | None
    added_by: str | None
    change_type: ChangeType


@dataclass(frozen=True)
class CurrentUser:
    """The authenticated user's own profile."""

    user_id: str
    display_name: str

    @classmethod
    def from_api(cls, payload: Mapping[str, Any]) -> CurrentUser:
        display_name = _text(payload.get("display_name"))
        return cls(
            user_id=_text(payload.get("id")),
            display_name=display_name or _text(payload.get("id")),
        )


@dataclass(frozen=True)
class OverviewMetrics:
    """Aggregate counts shown in the dashboard KPI row."""

    playlist_count: int
    track_count: int
    events_24h: int
    last_polled_at: str | None


@dataclass(frozen=True)
class PlaylistMetrics:
    """KPI counts for a single tracked playlist."""

    total_tracks: int
    contributor_count: int
    added_24h: int
    removed_24h: int
    last_polled_at: str | None


@dataclass(frozen=True)
class SyncResult:
    """Outcome of one observer poll cycle."""

    playlists_seen: int
    events_added: int
    error: str | None
