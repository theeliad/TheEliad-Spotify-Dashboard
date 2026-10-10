"""Estimate BPM from a local audio file.

Pure DSP: no database and no network access. librosa is imported lazily so the
rest of the application (and the test suite) does not depend on it.
"""

from __future__ import annotations

import importlib
from pathlib import Path
from types import ModuleType

import numpy as np

_MIN_BPM = 60.0
_MAX_BPM = 200.0
_INSTALL_HINT = "tempo estimation requires librosa; install it with 'pip install librosa soundfile'"


def _load_librosa() -> ModuleType:
    """Import librosa or raise a clear error explaining how to install it."""
    try:
        return importlib.import_module("librosa")
    except ImportError as exc:
        raise RuntimeError(_INSTALL_HINT) from exc


def ensure_available() -> None:
    """Raise RuntimeError when the DSP backend is not installed."""
    _load_librosa()


def _normalize(bpm: float) -> float:
    """Fold a tempo into the [_MIN_BPM, _MAX_BPM] range (half/double-time)."""
    while bpm < _MIN_BPM:
        bpm *= 2.0
    while bpm > _MAX_BPM:
        bpm /= 2.0
    return round(bpm, 1)


def estimate_tempo(path: Path) -> float | None:
    """Return the estimated tempo in BPM for an audio file, or None if unknown."""
    librosa = _load_librosa()
    samples, sample_rate = librosa.load(str(path), sr=None, mono=True)
    if samples.size == 0:
        return None
    tempo, _ = librosa.beat.beat_track(y=samples, sr=sample_rate)
    bpm = float(np.ravel(tempo)[0])
    if bpm <= 0:
        return None
    return _normalize(bpm)
