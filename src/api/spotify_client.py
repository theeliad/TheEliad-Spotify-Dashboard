"""Construction of the authenticated Spotify client. The only spotipy entry point."""

from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth, SpotifyOauthError

from src.settings import SCOPES, Settings

_TOKEN_FILENAME = "spotify_token.json"


def build_oauth_manager(settings: Settings, *, open_browser: bool = True) -> SpotifyOAuth:
    """Return a SpotifyOAuth manager sharing one cached token across the app."""
    settings.cache_path.mkdir(parents=True, exist_ok=True)
    return SpotifyOAuth(
        client_id=settings.client_id,
        client_secret=settings.client_secret,
        redirect_uri=settings.redirect_uri,
        scope=" ".join(SCOPES),
        cache_path=str(settings.cache_path / _TOKEN_FILENAME),
        open_browser=open_browser,
    )


def build_spotify_client(settings: Settings) -> Spotify:
    """Return an authenticated Spotify client using the OAuth user flow."""
    return Spotify(auth_manager=build_oauth_manager(settings))


def get_authorize_url(settings: Settings) -> str:
    """Return the Spotify login URL the user must visit to grant access."""
    return build_oauth_manager(settings, open_browser=False).get_authorize_url()


def exchange_code_for_token(settings: Settings, code: str) -> None:
    """Exchange an OAuth authorization code for a cached access token."""
    build_oauth_manager(settings, open_browser=False).get_access_token(
        code=code, as_dict=False
    )


def has_cached_token(settings: Settings) -> bool:
    """Return whether a usable token is already cached."""
    try:
        return build_oauth_manager(settings, open_browser=False).get_cached_token() is not None
    except SpotifyOauthError:
        return False
