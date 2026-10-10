"""Resolve and download 30-second audio previews from Deezer and iTunes.

This is the only non-Spotify outbound API in the application. Deezer is tried
first (its search response carries the preview URL); iTunes is the fallback.
"""

from __future__ import annotations

import logging
from pathlib import Path

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from src.schemas import Preview

logger = logging.getLogger(__name__)

_TIMEOUT_SECONDS = 15.0
_DEEZER_SEARCH_URL = "https://api.deezer.com/search"
_ITUNES_SEARCH_URL = "https://itunes.apple.com/search"
_HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}


def _session() -> requests.Session:
    """Return a session that retries transient 429/5xx responses on GET."""
    session = requests.Session()
    session.headers.update(_HEADERS)
    retry = Retry(
        total=2,
        backoff_factor=0.5,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset({"GET"}),
    )
    session.mount("https://", HTTPAdapter(max_retries=retry))
    return session


def _first_artist(artists: str) -> str:
    """Return the primary artist from a comma-separated artist string."""
    return artists.split(",")[0].strip()


def _duration_ms(value: object) -> int | None:
    """Convert a provider duration in whole seconds to milliseconds."""
    if isinstance(value, int) and value > 0:
        return value * 1000
    return None


def _deezer_preview(session: requests.Session, query: str) -> Preview | None:
    """Look a track up on Deezer and return its preview, if any."""
    response = session.get(
        _DEEZER_SEARCH_URL, params={"q": query, "limit": 1}, timeout=_TIMEOUT_SECONDS
    )
    response.raise_for_status()
    results = response.json().get("data") or []
    if not results:
        return None
    track = results[0]
    url = track.get("preview")
    if not isinstance(url, str) or not url:
        return None
    return Preview(url=url, duration_ms=_duration_ms(track.get("duration")))


def _itunes_preview(session: requests.Session, query: str) -> Preview | None:
    """Look a track up on iTunes and return its preview, if any."""
    response = session.get(
        _ITUNES_SEARCH_URL,
        params={"term": query, "entity": "song", "limit": 1},
        timeout=_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    results = response.json().get("results") or []
    if not results:
        return None
    track = results[0]
    url = track.get("previewUrl")
    if not isinstance(url, str) or not url:
        return None
    duration_ms = track.get("trackTimeMillis")
    return Preview(url=url, duration_ms=duration_ms if isinstance(duration_ms, int) else None)


def resolve_preview(track_name: str, artists: str) -> Preview | None:
    """Resolve a preview URL for a track via Deezer, falling back to iTunes.

    Returns None when both providers answer with no match. Raises
    requests.RequestException when every provider fails, so callers can retry
    rather than recording a permanent miss.
    """
    query = f"{track_name} {_first_artist(artists)}".strip()
    if not query:
        return None
    errors: list[requests.RequestException] = []
    with _session() as session:
        for lookup in (_deezer_preview, _itunes_preview):
            try:
                preview = lookup(session, query)
            except requests.RequestException as exc:
                logger.warning("preview lookup failed: %s", exc)
                errors.append(exc)
                continue
            if preview is not None:
                return preview
    if errors:
        raise errors[0]
    return None


def download_preview(url: str, destination: Path) -> None:
    """Download an audio preview to a local file."""
    with _session() as session:
        response = session.get(url, timeout=_TIMEOUT_SECONDS)
        response.raise_for_status()
        destination.write_bytes(response.content)
