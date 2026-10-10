"""One-time backfill of audio_features_cache tempo from track previews.

Resolves a 30-second preview for every playlist track that has no cache row,
estimates its tempo, and upserts the result. Tracks with no preview at all are
recorded with a NULL tempo so they are not retried; transient failures are
skipped so a later run can pick them up.
"""

from __future__ import annotations

import logging
import tempfile
from pathlib import Path

from src.api.fetch_preview import download_preview, resolve_preview
from src.db.db import db_connection
from src.db.load_uncached_tracks import load_uncached_tracks
from src.db.write_audio_features import write_audio_features
from src.schemas import AudioFeature, Track
from src.settings import Settings
from src.tempo.estimate import ensure_available, estimate_tempo

logger = logging.getLogger(__name__)


def backfill_tempos(settings: Settings, *, limit: int | None = None) -> int:
    """Populate tempo for uncached playlist tracks, returning rows written."""
    ensure_available()
    with db_connection(settings.db_path) as conn:
        tracks = load_uncached_tracks(conn)
        if limit is not None:
            tracks = tracks[:limit]
        features = [feature for track in tracks if (feature := _analyse(track)) is not None]
        write_audio_features(conn, features)
    return len(features)


def _analyse(track: Track) -> AudioFeature | None:
    """Return a cache feature for one track, or None when it should be retried."""
    try:
        preview = resolve_preview(track.track_name, track.artists)
    except Exception as exc:  # network/provider failure: retry on a later run
        logger.warning("preview resolution failed for %s: %s", track.track_uri, exc)
        return None
    if preview is None:
        return AudioFeature(track.track_uri, None, None)
    try:
        with tempfile.TemporaryDirectory() as tmp:
            audio_path = Path(tmp) / "preview.mp3"
            download_preview(preview.url, audio_path)
            tempo = estimate_tempo(audio_path)
    except Exception as exc:  # download/decode failure: retry on a later run
        logger.warning("tempo estimation failed for %s: %s", track.track_uri, exc)
        return None
    return AudioFeature(track.track_uri, tempo, preview.duration_ms)
