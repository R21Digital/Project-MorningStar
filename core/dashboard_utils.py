"""Shared utilities for building dashboard summaries."""

from __future__ import annotations

from typing import Iterable, Dict, List
from rich.console import Console
from rich.table import Table

from .quest_state import get_step_status
from .themepark_tracker import get_themepark_status
from .utils import render_progress_bar


def group_quests_by_category(
    legacy_steps: Iterable[dict] | None = None,
    themepark_quests: Iterable[str] | None = None,
) -> Dict[str, List[str]]:
    """Return a mapping of category name to status emoji list."""
    categories: Dict[str, List[str]] = {}
    if legacy_steps:
        for step in legacy_steps:
            cat = step.get("category", "Legacy")
            categories.setdefault(cat, []).append(get_step_status(step))
    if themepark_quests:
        categories["Theme Parks"] = [get_themepark_status(q) for q in themepark_quests]
    return categories


def build_summary_table(categories: Dict[str, List[str]]) -> Table:
    """Return a ``rich`` table showing progress bars and total counts."""
    table = Table(title="Quest Progress Summary")
    table.add_column("Category", style="bold")
    table.add_column("Progress")
    table.add_column("Count", justify="right")
    for cat, statuses in categories.items():
        table.add_row(cat, render_progress_bar(statuses), str(len(statuses)))
    return table


def print_summary_counts(categories: Dict[str, List[str]]) -> None:
    """Render a progress summary table using :func:`Console.print`."""
    Console().print(build_summary_table(categories))


__all__ = ["group_quests_by_category", "build_summary_table", "print_summary_counts"]
