"""Tests for the tempo backfill orchestrator (network and DSP are stubbed)."""

from pathlib import Path

import pytest

from src.db.load_playlist_tempo import load_playlist_tempo
from src.db.write_playlist import write_playlist
from src.db.write_playlist_tracks import write_playlist_tracks
from src.schemas import Preview
from src.settings import Settings
from src.tempo import backfill

_PREVIEW = Preview("http://provider/preview.mp3", 200000)


def _settings(db_path: Path) -> Settings:
    return Settings(
        client_id="id",
        client_secret="secret",
        redirect_uri="http://127.0.0.1:8501",
        db_path=db_path,
        cache_path=db_path.parent / ".cache",
    )


def _seed(db_conn, sample_playlist, sample_tracks) -> None:
    write_playlist(db_conn, sample_playlist, "2024-01-01 00:00:00")
    write_playlist_tracks(db_conn, sample_playlist.playlist_id, sample_tracks)
    db_conn.commit()


def _stub(monkeypatch: pytest.MonkeyPatch, *, tempo: float = 120.0, preview=_PREVIEW) -> None:
    monkeypatch.setattr(backfill, "ensure_available", lambda: None)
    monkeypatch.setattr(backfill, "resolve_preview", lambda name, artists: preview)
    monkeypatch.setattr(backfill, "download_preview", lambda url, dest: None)
    monkeypatch.setattr(backfill, "estimate_tempo", lambda path: tempo)


def test_backfill_writes_tempo_for_uncached_tracks(
    db_conn, tmp_db_path, sample_playlist, sample_tracks, monkeypatch: pytest.MonkeyPatch
) -> None:
    _seed(db_conn, sample_playlist, sample_tracks)
    _stub(monkeypatch, tempo=128.0)
    assert backfill.backfill_tempos(_settings(tmp_db_path)) == 2
    tempo = load_playlist_tempo(sample_playlist.playlist_id)
    assert list(tempo["tempo"]) == [128.0, 128.0]


def test_backfill_records_missing_preview_as_null_and_is_idempotent(
    db_conn, tmp_db_path, sample_playlist, sample_tracks, monkeypatch: pytest.MonkeyPatch
) -> None:
    _seed(db_conn, sample_playlist, sample_tracks)
    _stub(monkeypatch, preview=None)
    assert backfill.backfill_tempos(_settings(tmp_db_path)) == 2
    tempo = load_playlist_tempo(sample_playlist.playlist_id)
    assert tempo["tempo"].isna().all()
    assert backfill.backfill_tempos(_settings(tmp_db_path)) == 0


def test_backfill_skips_track_when_resolution_fails(
    db_conn, tmp_db_path, sample_playlist, sample_tracks, monkeypatch: pytest.MonkeyPatch
) -> None:
    _seed(db_conn, sample_playlist, sample_tracks)
    monkeypatch.setattr(backfill, "ensure_available", lambda: None)

    def boom(name: str, artists: str) -> Preview:
        raise RuntimeError("network down")

    monkeypatch.setattr(backfill, "resolve_preview", boom)
    assert backfill.backfill_tempos(_settings(tmp_db_path)) == 0
    tempo = load_playlist_tempo(sample_playlist.playlist_id)
    assert tempo["tempo"].isna().all()


def test_backfill_respects_limit(
    db_conn, tmp_db_path, sample_playlist, sample_tracks, monkeypatch: pytest.MonkeyPatch
) -> None:
    _seed(db_conn, sample_playlist, sample_tracks)
    _stub(monkeypatch)
    assert backfill.backfill_tempos(_settings(tmp_db_path), limit=1) == 1


def test_backfill_returns_zero_when_nothing_uncached(
    tmp_db_path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(backfill, "ensure_available", lambda: None)
    assert backfill.backfill_tempos(_settings(tmp_db_path)) == 0
