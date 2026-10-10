"""SQLite connection layer. Only module allowed to open the database."""

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from src.settings import load_db_path

_SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql"


def get_db_connection(db_path: Path | None = None) -> sqlite3.Connection:
    """Return a SQLite connection with row access by column name."""
    resolved_path = db_path if db_path is not None else load_db_path()
    _init_db(resolved_path)
    conn = sqlite3.connect(str(resolved_path), timeout=5.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


@contextmanager
def db_connection(db_path: Path | None = None) -> Iterator[sqlite3.Connection]:
    """Yield a connection, committing on success and rolling back on error."""
    conn = get_db_connection(db_path)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def _ensure_column(conn: sqlite3.Connection, table: str, column: str, ddl: str) -> None:
    """Add a column to an existing table when it is missing (schema evolution)."""
    existing = {row[1] for row in conn.execute(f"PRAGMA table_info({table})")}
    if column not in existing:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {ddl}")


def _init_db(db_path: Path) -> None:
    """Create tables from schema.sql if they do not yet exist."""
    conn = sqlite3.connect(str(db_path))
    try:
        schema = _SCHEMA_PATH.read_text(encoding="utf-8")
        conn.executescript(schema)
        _ensure_column(conn, "audio_features_cache", "duration_ms", "INTEGER")
        _ensure_column(conn, "playlist_tracks", "popularity", "INTEGER")
        conn.commit()
    finally:
        conn.close()
