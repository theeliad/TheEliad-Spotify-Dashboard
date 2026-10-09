"""Entry point: run one observer poll cycle."""

import sys

from src.observer.sync import run_sync
from src.settings import load_settings


def main() -> int:
    """Run one poll cycle and report the outcome."""
    result = run_sync(load_settings())
    print(
        f"playlists_seen={result.playlists_seen} "
        f"events_added={result.events_added} error={result.error}"
    )
    return 1 if result.error else 0


if __name__ == "__main__":
    sys.exit(main())
