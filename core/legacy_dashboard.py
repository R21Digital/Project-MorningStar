"""Utilities for displaying legacy quest progress."""

from __future__ import annotations

from rich.console import Console
from rich.table import Table

from .legacy_tracker import load_legacy_steps
from .quest_state import get_step_status


def display_legacy_progress() -> None:
    """Print a table of legacy quest steps and completion status."""
    steps = load_legacy_steps()

    table = Table(title="Legacy Quest Progress")
    table.add_column("ID", style="bold", no_wrap=True)
    table.add_column("Title")
    table.add_column("Status", justify="center")

    for step in steps:
        step_id = str(step.get("id"))
        title = step.get("title") or step.get("description", "")
        status = get_step_status(step_id)
        table.add_row(step_id, title, status)

    Console().print(table)


__all__ = ["display_legacy_progress"]
