"""Execute quests composed of basic step dictionaries."""

from __future__ import annotations

from typing import Any, Callable, Dict, Iterable
import time

from .engine.quest_executor import run_step_with_feedback


def _iter_steps(quest: Any) -> Iterable[dict]:
    if isinstance(quest, dict):
        steps = quest.get("steps", [])
    else:
        steps = getattr(quest, "steps", [])
    return steps or []


def run_steps(
    steps: Iterable[dict],
    *,
    dry_run: bool = False,
    delay: float = 0.0,
    log_fn: Callable[[str], None] = print,
    formatter: Callable[[int, dict], str] | None = None,
) -> None:
    """Execute a sequence of quest ``steps``.

    Parameters
    ----------
    steps:
        Iterable of step dictionaries.
    dry_run:
        When ``True`` step handlers are not invoked.
    delay:
        Optional delay between step executions.
    log_fn:
        Logging function used for step messages.
    formatter:
        Optional callable to format log messages given ``index`` and ``step``.
    """

    if formatter is None:
        formatter = lambda i, s: f"\u27A1\uFE0F Step {i}: {s.get('type') if isinstance(s, dict) else s}"

    for i, step in enumerate(steps, start=1):
        log_fn(formatter(i, step))
        if dry_run:
            continue
        if not run_step_with_feedback(step):
            action = step.get("type") if isinstance(step, dict) else None
            log_fn(f"\u26A0\uFE0F Step validation failed: {action}")
            continue
        
        if delay:
            time.sleep(delay)


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
        run_steps(_iter_steps(quest), dry_run=dry_run)
        status["completed"] = True
    except Exception as exc:  # pragma: no cover - unexpected failures
        print(f"\u26A0\uFE0F Error executing quest: {exc}")
        status["failed"] = True
    finally:
        status["in_progress"] = False

    return status
