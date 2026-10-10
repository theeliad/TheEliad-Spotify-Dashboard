"""Record one immutable playlist metadata snapshot per observed snapshot_id."""

import sqlite3

from src.schemas import PlaylistMeta

_INSERT = """
INSERT OR IGNORE INTO playlist_meta_snapshots (
    playlist_id, name, owner_id, owner_display_name,
    follower_count, collaborative, snapshot_id, captured_at
) VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
"""


def write_playlist_meta(conn: sqlite3.Connection, meta: PlaylistMeta) -> None:
    """Insert a metadata snapshot, skipping a snapshot_id already recorded."""
    conn.execute(
        _INSERT,
        (
            meta.playlist_id,
            meta.name,
            meta.owner_id,
            meta.owner_display_name,
            meta.follower_count,
            int(meta.collaborative),
            meta.snapshot_id,
        ),
    )
