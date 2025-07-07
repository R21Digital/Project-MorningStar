"""CLI entry point for legacy quest utilities."""

from __future__ import annotations

import argparse

from core.legacy_loop import run_full_legacy_quest
from core.legacy_dashboard import display_legacy_progress
from core.legacy_tracker import load_legacy_steps
from core.themepark_dashboard import display_themepark_progress
from core.themepark_tracker import load_themepark_chains
from core.unified_dashboard import show_unified_dashboard
from core.constants import VALID_STATUS_EMOJIS


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
    parser.add_argument(
        "--show-themepark-status",
        dest="show_themepark_status",
        action="store_true",
        help="Display current theme park quest progress",
    )
    parser.add_argument(
        "--show-dashboard",
        dest="show_dashboard",
        action="store_true",
        help="Display a unified quest progress dashboard",
    )
    parser.add_argument(
        "--dashboard-mode",
        choices=["legacy", "themepark", "all"],
        default="all",
        help="Select sections to display in the dashboard",
    )
    view_group = parser.add_mutually_exclusive_group()
    view_group.add_argument(
        "--summary",
        dest="summary",
        action="store_true",
        help="Show a summarized dashboard view",
    )
    view_group.add_argument(
        "--detailed",
        dest="summary",
        action="store_false",
        help="Show a detailed dashboard view (default)",
    )
    parser.set_defaults(summary=False)
    parser.add_argument(
        "--filter",
        dest="filter",
        metavar="EMOJI",
        help="Only show quest steps with the given status emoji",
    )
    args = parser.parse_args(argv)
    if args.filter and args.filter not in VALID_STATUS_EMOJIS:
        parser.error(
            f"Invalid emoji {args.filter!r}. Expected one of {', '.join(sorted(VALID_STATUS_EMOJIS))}"
        )
    return args


def main(argv: list[str] | None = None) -> None:
    """Execute actions based on CLI flags."""
    args = parse_args(argv)

    if args.show_legacy_status:
        steps = load_legacy_steps()
        display_legacy_progress(steps)

    if args.show_themepark_status:
        display_themepark_progress(load_themepark_chains())

    if args.show_dashboard:
        show_unified_dashboard(
            mode=args.dashboard_mode,
            summary=args.summary,
            filter_emoji=args.filter,
        )
        return

    if args.legacy or not (args.legacy or args.show_legacy_status or args.show_themepark_status):
        run_full_legacy_quest()


if __name__ == "__main__":
    main()
