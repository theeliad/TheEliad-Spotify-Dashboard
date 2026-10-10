# Spotify Playlist Dashboard

Streamlit dashboard + polling agents over the Spotify Web API.
Python 3.11.17, conda env `spotify_env`.

## Commands
- Activate: `conda activate spotify_env`
- Run app:  `streamlit run src/dashboard/main.py`
- Test one file: `pytest tests/test_spotify_client.py -x`
- Full test: `pytest -q`
- Lint:      `ruff check src/`
- Format:    `ruff format src/`

## Architecture
- Package root is src/. Imports read src.api.*, src.db.*, src.dashboard.*, 
  src.observer.* WITH the src prefix. This provides namespace isolation and 
  prevents collision with same-named PyPI packages.
- `src/api/` — ONLY place that touches spotipy. No API calls elsewhere.
- `src/db/`  — ONLY place that opens SQLite. Schema is append-only.
- `src/dashboard/` — reads from SQLite. Never calls the Spotify API directly.
- `src/observer/` — polling logic. Writes events to SQLite.
- Data shapes live in `src/schemas.py`. Settings loading lives in `src/settings.py`.
  Do not rename these to models.py or config.py (PyPI collision risk).
- All agents write events to SQLite; the dashboard is a pure reader.

## Clean code standards (non-negotiable)

### Philosophy
- Write the smallest function that passes the test. Nothing more.
- Less is more. If a variable, helper, or abstraction doesn't change behavior,
  remove it.
- Prefer standard library over third-party when the gap is small.

### String formatting
- Use f-strings for all string interpolation. No `.format()`, no `%` formatting.
- For multi-line strings, use triple-quoted f-strings.

### Typing
- Type-hint every public function signature: parameters and return type.
- Use `typing.Optional[T]` for Python 3.10 compatibility.
- Use `NamedTuple` or `dataclass` for structured return values, not `dict`.

### Efficiency
- No redundant loops. One pass when possible.
- Cache API responses locally. Never refetch the same data twice in one cycle.

### Error handling
- Catch specific exceptions. No bare `except:`.
- Never silently swallow errors.

### Caching discipline
- Every function that reads from SQLite **must** use `@st.cache_data` — never `@st.cache_resource`.
- Every function that reads from Spotify API **must** use `@st.cache_data` with `ttl=300` (5 minutes).
- Never use `@st.cache_resource` — it bypasses the human gate.
- If a function reads from both SQLite and Spotify, it must use `@st.cache_data` and include `ttl=300` to prevent stale data.

### Naming
- Variables: descriptive nouns. `user_playlist_ids` not `x`.
- Functions: verb + object. `fetch_playlist_tracks`.
- Booleans: `is_...` or `has_...` prefix.
- Constants: UPPER_SNAKE_CASE.

### Forbidden patterns
- No default exports without purpose.
- No complex expressions inside f-strings. Extract them first.
- No unused imports. Verify with `ruff check`.
- No nested f-strings.

## Streamlit architecture (non-negotiable)
- `src/dashboard/main.py` — Dashboard wiring only: imports, layout, interaction.
  NO API calls, NO SQL queries, NO data transformation.
- `src/dashboard/widgets/` — One `.py` file per major widget. Each contains:
    - `@st.cache_data`-decorated data functions
    - `render_<name>(df)` function that draws a single UI element
- Widget modules contain NO `st.sidebar`, NO `st.button`, NO `st.selectbox`.
- Every function that reads SQLite or calls the API MUST use `@st.cache_data`.
- No widget module calls another widget module's render function.

## Meta-agent lockdown (non-negotiable)
- No agent may create, edit, rename, or delete anything under
  `.opencode/agents/`, `AGENTS.md`, or `opencode.json`. These are human-owned.
- No agent may modify this file. Propose changes as a diff in chat only.
- No agent may invoke another agent to work around a denied permission.
  If a task requires capability you lack, STOP and report it.
- No agent may install packages, add channels, or alter `spotify_env.yml`.
- An agent may propose changes to constitution files as a diff. It may never
  apply them. Applying is a human action performed in an editor.

## Failure protocol
- Maximum 3 repair attempts per failing test. On the third failure, stop.
- Write attempt history to review-reports/YYYY-MM-DD-blocked.md.
- Present the report and wait for direction. Do not begin a fourth attempt.
- Never weaken or delete a test to make it pass. Report it, don't edit it.

## Spotify API constraints
- No webhooks exist. All change detection = polling + snapshot_id diff.
- `added_at` / `added_by` require USER auth (SpotifyOAuth), not client credentials.
- Required scopes: playlist-read-private, playlist-read-collaborative,
  user-library-read, user-read-recently-played.
- Respect rate limits. Back off on HTTP 429 using Retry-After header.
- Never call PUT/POST/DELETE against Spotify endpoints. Read-only only.

## TODO(ai) convention
- When I write `//TODO(ai): <description>`, treat it as a structural debt ticket.
  Prioritize it above feature work. Fix it in the same PR that touches the
  surrounding code. Do not defer it.
  
## Sanctioned Exception: OAuth Flow

- The dashboard may **sanctioned** use a single module `src/dashboard/connect.py`
  to handle user authentication with Spotify.
- This module **may** call `src/api/` helper functions **only** to fetch playlists/tracks.
- It **must not** directly import `spotipy` or make raw Spotify API calls.
- The OAuth flow must:
  1. Use `st.query_params` to receive the OAuth `code` from Spotify's redirect.
  2. Exchange that code for a token via `spotipy.oauth2.SpotifyOAuth`.
  3. Cache the token in `.cache/spotify_token.json` (shared with observer).
  4. Store the **connected playlist IDs** in `tracked_playlists` table.
- The observer **only polls playlists listed in `tracked_playlists`**.
- The dashboard **only reads from SQLite** — never calls Spotify again after login.
- The redirect URI **must be set in the Spotify Developer Console** to:
  `http://127.0.0.1:8501` (Streamlit's default port).
- The `.env` file must contain:
  ```env
  SPOTIFY_REDIRECT_URI=http://127.0.0.1:8501