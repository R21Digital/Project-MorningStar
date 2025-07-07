"""CLI entry point for legacy quest utilities."""

from __future__ import annotations

import argparse

from core.legacy_loop import run_full_legacy_quest
from core.legacy_dashboard import display_legacy_progress, show_legacy_dashboard
from core.legacy_tracker import load_legacy_steps
from core.themepark_dashboard import display_themepark_progress
from core.themepark_tracker import load_themepark_chains
from core.unified_dashboard import show_unified_dashboard


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
    parser.add_argument(
        "--filter-status",
        dest="filter_status",
        help="Only display rows matching the given status emoji",
    )
    return parser.parse_args(argv)


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
            mode=args.dashboard_mode, filter_status=args.filter_status
        )
        return

    if args.legacy or not (args.legacy or args.show_legacy_status or args.show_themepark_status):
        run_full_legacy_quest()


if __name__ == "__main__":
    main()
