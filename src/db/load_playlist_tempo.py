"""Read a playlist's tracks with cached tempo and duration, in playlist order."""

import pandas as pd

from src.db.db import db_connection

_QUERY = (
    "SELECT pt.position, pt.track_name, pt.artists, af.tempo, af.duration_ms "
    "FROM playlist_tracks AS pt "
    "LEFT JOIN audio_features_cache AS af ON af.track_uri = pt.track_uri "
    "WHERE pt.playlist_id = ? ORDER BY pt.position"
)


def load_playlist_tempo(playlist_id: str) -> pd.DataFrame:
    """Return one playlist's tracks with tempo/duration joined in position order."""
    with db_connection() as conn:
        return pd.read_sql_query(_QUERY, conn, params=(playlist_id,))
