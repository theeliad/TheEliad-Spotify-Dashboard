"""Tests for audio-preview resolution and download."""

import pytest
import requests

from src.api import fetch_preview
from src.schemas import Preview


class _NoopSession:
    def __enter__(self) -> "_NoopSession":
        return self

    def __exit__(self, *exc: object) -> bool:
        return False


def test_resolve_prefers_deezer(monkeypatch: pytest.MonkeyPatch) -> None:
    deezer = Preview("http://deezer/preview.mp3", 200000)
    monkeypatch.setattr(fetch_preview, "_session", _NoopSession)
    monkeypatch.setattr(fetch_preview, "_deezer_preview", lambda session, query: deezer)
    monkeypatch.setattr(
        fetch_preview, "_itunes_preview", lambda session, query: pytest.fail("no fallback expected")
    )
    assert fetch_preview.resolve_preview("Song", "Artist") == deezer


def test_resolve_falls_back_to_itunes(monkeypatch: pytest.MonkeyPatch) -> None:
    itunes = Preview("http://itunes/preview.m4a", 180000)
    monkeypatch.setattr(fetch_preview, "_session", _NoopSession)
    monkeypatch.setattr(fetch_preview, "_deezer_preview", lambda session, query: None)
    monkeypatch.setattr(fetch_preview, "_itunes_preview", lambda session, query: itunes)
    assert fetch_preview.resolve_preview("Song", "Artist") == itunes


def test_resolve_returns_none_when_no_match(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(fetch_preview, "_session", _NoopSession)
    monkeypatch.setattr(fetch_preview, "_deezer_preview", lambda session, query: None)
    monkeypatch.setattr(fetch_preview, "_itunes_preview", lambda session, query: None)
    assert fetch_preview.resolve_preview("Song", "Artist") is None


def test_resolve_returns_none_for_empty_query() -> None:
    assert fetch_preview.resolve_preview("", "") is None


def test_resolve_falls_back_when_deezer_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    itunes = Preview("http://itunes/preview.m4a", 180000)

    def boom(session: object, query: str) -> Preview:
        raise requests.RequestException("deezer down")

    monkeypatch.setattr(fetch_preview, "_session", _NoopSession)
    monkeypatch.setattr(fetch_preview, "_deezer_preview", boom)
    monkeypatch.setattr(fetch_preview, "_itunes_preview", lambda session, query: itunes)
    assert fetch_preview.resolve_preview("Song", "Artist") == itunes


def test_resolve_raises_when_all_providers_fail(monkeypatch: pytest.MonkeyPatch) -> None:
    def boom(session: object, query: str) -> Preview:
        raise requests.RequestException("down")

    monkeypatch.setattr(fetch_preview, "_session", _NoopSession)
    monkeypatch.setattr(fetch_preview, "_deezer_preview", boom)
    monkeypatch.setattr(fetch_preview, "_itunes_preview", boom)
    with pytest.raises(requests.RequestException):
        fetch_preview.resolve_preview("Song", "Artist")


def test_download_preview_writes_file(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    class _Response:
        content = b"audio-bytes"

        def raise_for_status(self) -> None:
            return None

    class _Session:
        def __enter__(self) -> "_Session":
            return self

        def __exit__(self, *exc: object) -> bool:
            return False

        def get(self, url: str, timeout: float) -> _Response:
            return _Response()

    monkeypatch.setattr(fetch_preview, "_session", _Session)
    destination = tmp_path / "preview.mp3"
    fetch_preview.download_preview("http://x/preview.mp3", destination)
    assert destination.read_bytes() == b"audio-bytes"
