"""CLI entry point for legacy quest utilities."""

from __future__ import annotations

import argparse

from core.legacy_loop import run_full_legacy_quest
from core.legacy_dashboard import display_legacy_progress


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Return parsed command line arguments."""
    parser = argparse.ArgumentParser(description="Legacy quest utilities")
    parser.add_argument(
        "--legacy",
        action="store_true",
        help="Run the full legacy quest loop",
    )
    parser.add_argument(
        "--show-legacy-status",
        dest="show_legacy_status",
        action="store_true",
        help="Display current legacy quest progress",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    """Execute actions based on CLI flags."""
    args = parse_args(argv)

    if args.show_legacy_status:
        display_legacy_progress()

    if args.legacy or not (args.legacy or args.show_legacy_status):
        run_full_legacy_quest()


if __name__ == "__main__":
    main()
