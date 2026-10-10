"""Tests for tempo persistence and per-playlist tempo reads."""

import pandas as pd
from streamlit.testing.v1 import AppTest

from src.dashboard.widgets.playlist_bpm import _bpm_figure
from src.db.load_playlist_tempo import load_playlist_tempo
from src.db.write_audio_features import write_audio_features
from src.db.write_playlist import write_playlist
from src.db.write_playlist_tracks import write_playlist_tracks
from src.schemas import AudioFeature

_EMPTY_BPM_APP = """
import pandas as pd

from src.dashboard.widgets.playlist_bpm import render_playlist_bpm

frame = pd.DataFrame(columns=["position", "track_name", "artists", "tempo", "duration_ms"])
render_playlist_bpm(frame)
"""


def test_write_audio_features_inserts_then_updates(
    db_conn, sample_playlist, sample_tracks
) -> None:
    write_playlist(db_conn, sample_playlist, "2024-01-01 00:00:00")
    write_playlist_tracks(db_conn, sample_playlist.playlist_id, sample_tracks)
    write_audio_features(db_conn, [AudioFeature("spotify:track:a", 120.0, 200000)])
    db_conn.commit()

    write_audio_features(db_conn, [AudioFeature("spotify:track:a", 125.5, 210000)])
    db_conn.commit()

    tempo = load_playlist_tempo(sample_playlist.playlist_id)
    assert tempo.iloc[0]["tempo"] == 125.5
    assert tempo.iloc[0]["duration_ms"] == 210000


def test_load_playlist_tempo_joins_in_position_order_with_nulls(
    db_conn, sample_playlist, sample_tracks
) -> None:
    write_playlist(db_conn, sample_playlist, "2024-01-01 00:00:00")
    write_playlist_tracks(db_conn, sample_playlist.playlist_id, sample_tracks)
    write_audio_features(db_conn, [AudioFeature("spotify:track:b", 90.0, 180000)])
    db_conn.commit()

    tempo = load_playlist_tempo(sample_playlist.playlist_id)
    assert list(tempo["track_name"]) == ["Alpha", "Beta"]
    assert pd.isna(tempo.iloc[0]["tempo"])
    assert tempo.iloc[1]["tempo"] == 90.0


def test_render_playlist_bpm_shows_info_when_empty() -> None:
    app = AppTest.from_string(_EMPTY_BPM_APP).run()
    assert not app.exception
    assert app.info[0].value == (
        "No tempo data for this playlist yet. Run `python -m src.tempo` to backfill."
    )


def test_bpm_figure_uses_positions_and_keeps_gaps() -> None:
    frame = pd.DataFrame(
        {
            "position": [1, 2, 3, 4, 5],
            "track_name": ["a", "b", "c", "d", "e"],
            "artists": ["x"] * 5,
            "tempo": [120.0, None, 130.0, 140.0, None],
            "duration_ms": [1] * 5,
        }
    )
    figure = _bpm_figure(frame)
    assert list(figure.data[0].x) == [1, 2, 3, 4, 5]
    assert sum(pd.isna(v) for v in figure.data[0].y) == 2
    assert figure.data[0].connectgaps in (None, False)
