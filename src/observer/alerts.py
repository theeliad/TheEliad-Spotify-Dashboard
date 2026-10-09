"""Write alert payloads for detected changes as JSON files."""

import json
from collections.abc import Sequence
from pathlib import Path

from src.schemas import TrackEvent
from src.settings import PROJECT_ROOT

_OUTBOX = PROJECT_ROOT / "alerts" / "outbox"


def write_alert_payload(events: Sequence[TrackEvent], run_id: int) -> Path | None:
    """Write one JSON payload for a non-empty change batch, returning its path."""
    if not events:
        return None
    _OUTBOX.mkdir(parents=True, exist_ok=True)
    path = _OUTBOX / f"{run_id}-{events[0].playlist_id}.json"
    payload = [
        {
            "playlist_id": event.playlist_id,
            "track_uri": event.track_uri,
            "track_name": event.track_name,
            "artists": event.artists,
            "change_type": event.change_type,
        }
        for event in events
    ]
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path
