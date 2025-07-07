"""Display legacy and theme park quest progress together using ``rich``."""

from __future__ import annotations

from rich.console import Console
from rich.layout import Layout

from .legacy_tracker import load_legacy_steps
from .legacy_dashboard import render_legacy_table
from .themepark_tracker import load_themepark_chains
from .themepark_dashboard import render_themepark_table


def show_unified_dashboard(
    themepark_quests: list[str] | None = None,
    *,
    mode: str = "all",
    legacy_steps: list | None = None,
) -> None:
    """Print a dashboard with quest progress based on ``mode``."""

    if legacy_steps is None:
        legacy_steps = load_legacy_steps()
    if themepark_quests is None:
        themepark_quests = load_themepark_chains()

    legacy_table = render_legacy_table(legacy_steps)
    themepark_table = render_themepark_table(themepark_quests)

    if mode == "legacy":
        Console().print(legacy_table)
        return
    if mode == "themepark":
        Console().print(themepark_table)
        return

    layout = Layout()
    layout.split_column(
        Layout(legacy_table, name="legacy"),
        Layout(themepark_table, name="themepark"),
    )

    Console().print(layout)


__all__ = ["show_unified_dashboard"]
