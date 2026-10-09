-- Spotify Playlist Dashboard schema
-- Append-only design: no UPDATE or DELETE in application code.

PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

-- One row per playlist, holding its last-seen snapshot for diffing.
CREATE TABLE IF NOT EXISTS playlists (
    playlist_id   TEXT PRIMARY KEY,
    name          TEXT NOT NULL,
    owner_id      TEXT,
    collaborative INTEGER NOT NULL DEFAULT 0,
    snapshot_id   TEXT,
    track_count   INTEGER NOT NULL DEFAULT 0,
    first_seen_at TEXT NOT NULL DEFAULT (datetime('now')),
    last_polled_at TEXT
);

-- Track membership as observed at poll time.
-- Replaced wholesale per playlist on each poll (delete + insert inside a txn).
CREATE TABLE IF NOT EXISTS playlist_tracks (
    playlist_id TEXT NOT NULL REFERENCES playlists(playlist_id),
    track_uri   TEXT NOT NULL,
    track_name  TEXT,
    artists     TEXT,
    album_name  TEXT,
    added_at    TEXT,
    added_by    TEXT,
    position    INTEGER,
    PRIMARY KEY (playlist_id, track_uri)
);

-- Immutable audit log of every detected change. Never modified after insert.
CREATE TABLE IF NOT EXISTS track_events (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    playlist_id TEXT NOT NULL,
    track_uri   TEXT NOT NULL,
    track_name  TEXT,
    artists     TEXT,
    added_at    TEXT,
    added_by    TEXT,
    change_type TEXT NOT NULL CHECK (change_type IN ('added', 'removed')),
    detected_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Cached audio features so we never refetch the same track twice.
CREATE TABLE IF NOT EXISTS audio_features_cache (
    track_uri        TEXT PRIMARY KEY,
    energy           REAL,
    danceability     REAL,
    valence          REAL,
    tempo            REAL,
    key              INTEGER,
    mode             INTEGER,
    acousticness     REAL,
    instrumentalness REAL,
    fetched_at       TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Poll-cycle bookkeeping for the observer agent.
CREATE TABLE IF NOT EXISTS poll_runs (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    started_at    TEXT NOT NULL,
    finished_at   TEXT,
    playlists_seen INTEGER NOT NULL DEFAULT 0,
    events_added  INTEGER NOT NULL DEFAULT 0,
    error         TEXT
);

CREATE INDEX IF NOT EXISTS idx_track_events_playlist_time
    ON track_events(playlist_id, detected_at DESC);

CREATE INDEX IF NOT EXISTS idx_track_events_type
    ON track_events(change_type);

CREATE INDEX IF NOT EXISTS idx_playlist_tracks_added_at
    ON playlist_tracks(added_at DESC);

-- Playlists the user explicitly connected through the OAuth flow. Append-only:
-- rows are inserted (never deleted), so the set of tracked playlists only grows.
CREATE TABLE IF NOT EXISTS tracked_playlists (
    playlist_id TEXT PRIMARY KEY,
    tracked_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Display names for known Spotify users. Spotify exposes only user ids on
-- tracks' added_by object, so names are cached here as they are learned.
CREATE TABLE IF NOT EXISTS app_users (
    user_id      TEXT PRIMARY KEY,
    display_name TEXT,
    fetched_at   TEXT NOT NULL DEFAULT (datetime('now'))
);