"""Helpers for running quest steps."""

from typing import Any, Dict


def execute_quest(quest: Any, *, dry_run: bool = False) -> Dict[str, bool]:
    """Execute the given ``quest``.

    Parameters
    ----------
    quest:
        The quest data which should contain a ``steps`` sequence.
    dry_run:
        If ``True`` no real automation is performed. Instead, each step is
        logged as if it were executed. This is useful for testing.

    Returns
    -------
    dict
        Status flags for the quest execution containing ``in_progress``,
        ``completed`` and ``failed`` keys.
    """
    print(f"[DEBUG] Executing quest: {quest}")

    status = {"in_progress": True, "completed": False, "failed": False}
    steps = getattr(quest, "steps", None) or quest.get("steps", []) if isinstance(quest, dict) else []

    try:
        for idx, step in enumerate(steps, start=1):
            prefix = "DRY-RUN" if dry_run else "STEP"
            print(f"[{prefix}] {idx}: {step}")
            # Real automation would occur here in non-dry-run mode

        status["completed"] = True
    except Exception as exc:  # pragma: no cover - unexpected failures
        print(f"[ERROR] {exc}")
        status["failed"] = True
    finally:
        status["in_progress"] = False

    return status
