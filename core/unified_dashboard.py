"""Display legacy and theme park quest progress together using ``rich``."""

from __future__ import annotations

from rich.console import Console
from rich.layout import Layout

from .legacy_tracker import load_legacy_steps
from .legacy_dashboard import build_legacy_progress_table
from .themepark_dashboard import build_themepark_progress_table


def show_unified_dashboard(themepark_quests: list[str]) -> None:
    """Print a dashboard with legacy and theme park progress."""

    steps = load_legacy_steps()
    legacy_table = build_legacy_progress_table(steps)
    themepark_table = build_themepark_progress_table(themepark_quests)

    layout = Layout()
    layout.split_column(
        Layout(legacy_table, name="legacy"),
        Layout(themepark_table, name="themepark"),
    )

    Console().print(layout)


__all__ = ["show_unified_dashboard"]
