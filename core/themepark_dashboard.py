"""Displays a progress table for Theme Park quests using the rich library."""

from __future__ import annotations

from rich.table import Table
from rich.console import Console

from .themepark_tracker import get_themepark_status


def build_themepark_progress_table(quests: list[str]) -> Table:
    """Return a table summarizing theme park quest ``quests`` progress."""

    table = Table(title="Theme Park Quest Progress")
    table.add_column("Quest", style="bold")
    table.add_column("Status", style="cyan")

    for quest in quests:
        status = get_themepark_status(quest)
        table.add_row(quest, status)

    return table


def display_themepark_progress(quests: list[str]) -> None:
    """Print a table of theme park ``quests`` and their status."""

    Console().print(build_themepark_progress_table(quests))


__all__ = ["build_themepark_progress_table", "display_themepark_progress"]
