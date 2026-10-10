"""Tests for tempo estimation (librosa is faked; no real audio required)."""

import sys
import types
from pathlib import Path

import numpy as np
import pytest

from src.tempo import estimate


def _fake_librosa(samples: np.ndarray, tempo: float) -> types.SimpleNamespace:
    beat = types.SimpleNamespace(beat_track=lambda y, sr: (tempo, None))
    load = lambda path, sr=None, mono=True: (samples, 22050)  # noqa: E731
    return types.SimpleNamespace(load=load, beat=beat)


def test_estimate_tempo_returns_bpm(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setitem(sys.modules, "librosa", _fake_librosa(np.ones(1000), 128.0))
    assert estimate.estimate_tempo(tmp_path / "a.mp3") == 128.0


def test_estimate_normalizes_double_time(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setitem(sys.modules, "librosa", _fake_librosa(np.ones(1000), 300.0))
    assert estimate.estimate_tempo(tmp_path / "a.mp3") == 150.0


def test_estimate_normalizes_half_time(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setitem(sys.modules, "librosa", _fake_librosa(np.ones(1000), 40.0))
    assert estimate.estimate_tempo(tmp_path / "a.mp3") == 80.0


def test_estimate_returns_none_for_empty_audio(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setitem(sys.modules, "librosa", _fake_librosa(np.array([]), 120.0))
    assert estimate.estimate_tempo(tmp_path / "a.mp3") is None


def test_ensure_available_raises_when_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setitem(sys.modules, "librosa", None)
    with pytest.raises(RuntimeError):
        estimate.ensure_available()
