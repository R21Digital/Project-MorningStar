"""Utilities for displaying legacy quest progress."""

from __future__ import annotations

from rich.console import Console
from rich.table import Table

from .quest_state import get_step_status


def build_legacy_progress_table(quest_steps: list) -> Table:
    """Return a ``rich`` table showing ``quest_steps`` progress."""

    table = Table(title="Legacy Quest Progress", show_lines=True)
    table.add_column("Step ID", style="bold", no_wrap=True)
    table.add_column("Step Name")
    table.add_column("Status", justify="center")

    for step in quest_steps:
        step_id = str(step.get("id"))
        title = step.get("title") or step.get("description", "")
        status = get_step_status(step_id)
        table.add_row(step_id, title, status)

    return table


def display_legacy_progress(quest_steps: list) -> None:
    """Print a table of ``quest_steps`` and completion status."""

    Console().print(build_legacy_progress_table(quest_steps))


__all__ = ["build_legacy_progress_table", "display_legacy_progress"]
