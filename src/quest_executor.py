"""Execute quests composed of basic step dictionaries."""

from __future__ import annotations

from typing import Any, Dict, Iterable

from .engine.quest_executor import run_step_with_feedback


def _iter_steps(quest: Any) -> Iterable[dict]:
    if isinstance(quest, dict):
        steps = quest.get("steps", [])
    else:
        steps = getattr(quest, "steps", [])
    return steps or []


def execute_quest(quest: Any, *, dry_run: bool = False) -> Dict[str, bool]:
    """Execute ``quest`` by dispatching each step type.

    Each step should be a dictionary containing a ``type`` key. When ``dry_run``
    is ``True`` the step handlers are not invoked and only the dispatch log is
    printed.
    """

    if isinstance(quest, dict):
        name = quest.get("name") or quest.get("title")
    else:
        name = getattr(quest, "name", None) or getattr(quest, "title", None)
    name = name or "Unknown"
    print(f"\U0001F680 Executing quest: {name}")

    status = {"in_progress": True, "completed": False, "failed": False}

    try:
        for idx, step in enumerate(_iter_steps(quest), start=1):
            action = step.get("type") if isinstance(step, dict) else None
            print(f"\u27A1\uFE0F Step {idx}: {action or step}")
            if dry_run:
                continue
            if not run_step_with_feedback(step):
                print(f"\u26A0\uFE0F Step validation failed: {action}")

        status["completed"] = True
    except Exception as exc:  # pragma: no cover - unexpected failures
        print(f"\u26A0\uFE0F Error executing quest: {exc}")
        status["failed"] = True
    finally:
        status["in_progress"] = False

    return status
