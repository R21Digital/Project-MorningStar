"""Helpers for running quest steps."""

from typing import Any


def execute_quest(quest: Any) -> None:
    """Execute the given ``quest``.

    Currently a stub that prints the quest and returns ``None``.
    """
    print(f"[DEBUG] Executing quest: {quest}")
    # TODO: iterate over quest steps and perform automation
    return None
