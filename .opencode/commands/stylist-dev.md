---
description: Repo-specific dev skill. Diagnose bugs, review changes, or plan
  maintenance against this project's known constraints. Never edits without
  approval.
agent: build
---

You are invoking the stylist-dev skill for the Spotify Playlist Dashboard repo.

## Invocation
$ARGUMENTS contains the bug report, broken behavior, or maintenance request.

## Diagnostic sequence (follow in order)

1. Run `ruff check src/` and `pytest -q` FIRST. Establish ground truth before
   theorizing. Do not guess at a cause you have not reproduced.
2. Read the failing traceback bottom-up. Identify the exact file and line.
3. Check the constraint table below before proposing any fix. If the fix would
   violate one, say so explicitly and propose an alternative that does not.
4. Propose the fix as a unified diff. Do NOT apply it. Wait for approval.

## Hard constraints of THIS repo

### Layering violations (most common bug source here)
- spotipy imports belong ONLY in `src/api/`. If found elsewhere, that IS the bug.
- sqlite3 imports belong ONLY in `src/db/db.py`.
- `src/dashboard/` must never import spotipy or sqlite3 directly.
- Widget modules must not contain st.sidebar, st.button, or st.selectbox.
  Those belong in main.py. A widget with UI state is misfiled code.

### Streamlit runtime quirks
- Streamlit reruns the ENTIRE script top-to-bottom on every interaction.
  An uncached data function re-executes on each click. This causes apparent
  "intermittent" slowness that is actually deterministic.
- @st.cache_data cannot hash unhashable args (dicts, DataFrames passed as keys).
  Pass primitives (playlist_id strings), not objects.
- Never read st.session_state inside a @st.cache_data function. The cache will
  return stale values across sessions silently.
- SQLite connections must close after use. Leaked handles lock the DB file and
  produce "database is locked" errors that look random.

### Spotify API realities
- No webhooks exist. Any "why didn't I get notified" question means polling
  timing, not a missed event.
- added_at and added_by return NULL under client-credentials auth. If they are
  empty, the OAuth scope set is wrong, not the parsing code.
- Required scopes: playlist-read-private, playlist-read-collaborative,
  user-library-read, user-read-recently-played. Missing scope = missing field.
- HTTP 429 requires honoring Retry-After. Aggressive retry makes it worse.
- Playlists cap at 10,000 items via offset pagination. Beyond that, data is
  silently truncated, not errored.

### Dependency pins (do not change without approval)
- Python 3.11.17 pinned in spotify_env.yml. Conda env name: spotify_env.
- spotipy==2.24.0 installed via nested pip block. 2.26.0 deprecates several
  methods; upgrading is a breaking change requiring a migration pass.
- pandas==2.2.2, streamlit==1.37.0 also pip-managed.
- numpy and plotly are conda-managed. Mixing install managers for these two
  causes ABI mismatches — always reinstall via the same manager.

### Files no agent may modify
- AGENTS.md, opencode.json, ruff.toml, spotify_env.yml
- .opencode/agents/* and .opencode/commands/*
- src/db/schema.sql destructively (migrations are additive only)

## Output contract

Report in exactly this structure:

**Symptom** — what was observed, quoted from the actual error.
**Root cause** — the specific mechanism, citing file:line.
**Constraint check** — which repo rules bear on this fix.
**Proposed diff** — fenced unified diff. Not applied.
**Verification** — the exact command to run after applying, and expected output.

If you cannot reproduce the bug, say so and list what information you need.
Do not invent a plausible-sounding cause to fill the format.

## Failure protocol
Three failed repair attempts maximum. On the third, write attempt history to
review-reports/YYYY-MM-DD-blocked.md and stop. Never weaken a test to pass it.