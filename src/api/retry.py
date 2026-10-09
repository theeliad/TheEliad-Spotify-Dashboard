"""Rate-limit-aware retry wrapper for Spotify API calls."""

import time
from collections.abc import Callable
from typing import TypeVar

from spotipy.exceptions import SpotifyException

T = TypeVar("T")

_MAX_RETRIES = 1
_DEFAULT_RETRY_AFTER = 1.0


def _retry_after_seconds(exc: SpotifyException) -> float:
    raw = (exc.headers or {}).get("Retry-After")
    try:
        return float(raw)
    except (TypeError, ValueError):
        return _DEFAULT_RETRY_AFTER


def call_with_backoff(call: Callable[[], T]) -> T:
    """Call a Spotify function, retrying once on HTTP 429 using Retry-After."""
    attempt = 0
    while True:
        try:
            return call()
        except SpotifyException as exc:
            if exc.http_status != 429 or attempt >= _MAX_RETRIES:
                raise
            attempt += 1
            time.sleep(_retry_after_seconds(exc))
