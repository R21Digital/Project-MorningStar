"""Display legacy and theme park quest progress together using ``rich``."""

from __future__ import annotations

from rich.console import Console
from rich.layout import Layout
from rich.table import Table

from .legacy_tracker import load_legacy_steps
from .legacy_dashboard import render_legacy_table
from .themepark_tracker import load_themepark_chains, get_themepark_status
from .themepark_dashboard import render_themepark_table
from .quest_state import get_step_status
from .dashboard_utils import build_summary_table, group_quests_by_category


def show_unified_dashboard(
    themepark_quests: list[str] | None = None,
    *,
    mode: str = "all",
    legacy_steps: list | None = None,
    summary: bool = False,
    filter_status: str | None = None,
) -> None:
    """Print a dashboard with quest progress based on ``mode``."""

    allowed_modes = {"legacy", "themepark", "all"}
    if mode not in allowed_modes:
        raise ValueError(
            f"Invalid mode '{mode}'. Expected one of {', '.join(sorted(allowed_modes))}"
        )

    if legacy_steps is None:
        legacy_steps = load_legacy_steps()
    if themepark_quests is None:
        themepark_quests = load_themepark_chains()

    if filter_status:
        if mode in {"legacy", "all"}:
            legacy_steps = [
                s for s in legacy_steps if get_step_status(s) == filter_status
            ]
        if mode in {"themepark", "all"}:
            themepark_quests = [
                q for q in themepark_quests if get_themepark_status(q) == filter_status
            ]

    if summary:
        categories = group_quests_by_category(
            legacy_steps if mode in {"legacy", "all"} else [],
            themepark_quests if mode in {"themepark", "all"} else [],
        )
        Console().print(build_summary_table(categories))
        return

    legacy_table = render_legacy_table(legacy_steps, summary=summary)
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
