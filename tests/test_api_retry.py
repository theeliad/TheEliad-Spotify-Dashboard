"""Tests for the Spotify API retry wrapper."""

import pytest
from spotipy.exceptions import SpotifyException

from src.api import retry


def _rate_limited() -> SpotifyException:
    return SpotifyException(429, -1, "rate limited", headers={"Retry-After": "2"})


def test_retries_once_then_succeeds(monkeypatch: pytest.MonkeyPatch) -> None:
    sleeps: list[float] = []
    monkeypatch.setattr(retry.time, "sleep", sleeps.append)
    attempts = {"count": 0}

    def call() -> str:
        attempts["count"] += 1
        if attempts["count"] == 1:
            raise _rate_limited()
        return "ok"

    assert retry.call_with_backoff(call) == "ok"
    assert attempts["count"] == 2
    assert sleeps == [2.0]


def test_non_429_raises_immediately(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(retry.time, "sleep", lambda seconds: None)
    attempts = {"count": 0}

    def call() -> str:
        attempts["count"] += 1
        raise SpotifyException(500, -1, "boom")

    with pytest.raises(SpotifyException):
        retry.call_with_backoff(call)
    assert attempts["count"] == 1


def test_gives_up_after_one_retry(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(retry.time, "sleep", lambda seconds: None)
    attempts = {"count": 0}

    def call() -> str:
        attempts["count"] += 1
        raise _rate_limited()

    with pytest.raises(SpotifyException):
        retry.call_with_backoff(call)
    assert attempts["count"] == 2
