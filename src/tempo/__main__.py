"""Entry point: one-time backfill of tempo from track previews."""

import argparse
import logging
import sys
import time

from src.settings import load_settings
from src.tempo.backfill import backfill_tempos


def _parse_limit(argv: list[str]) -> int | None:
    parser = argparse.ArgumentParser(
        description="Backfill audio_features_cache tempo from 30-second previews."
    )
    parser.add_argument(
        "--limit", type=int, default=None, help="maximum number of tracks to process"
    )
    return parser.parse_args(argv).limit


def main(argv: list[str] | None = None) -> int:
    """Run the tempo backfill and report how many rows were written."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    limit = _parse_limit(sys.argv[1:] if argv is None else argv)
    started = time.time()
    written = backfill_tempos(load_settings(), limit=limit)
    elapsed = time.time() - started
    print(f"rows_written={written} elapsed={elapsed:.0f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
