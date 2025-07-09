"""Display legacy and theme park quest progress together using ``rich``."""

from __future__ import annotations

from rich.console import Console

from profession_logic.utils.logger import log_info


from .legacy_tracker import load_legacy_steps
from .legacy_dashboard import render_legacy_table
from .themepark_tracker import load_themepark_chains, get_themepark_status
from .themepark_dashboard import render_themepark_table
from .quest_state import get_step_status
from .dashboard_utils import (
    build_summary_table,
    group_quests_by_category,
    group_steps_by_category,
    summarize_status_counts,
    calculate_completion_percentage,
)


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

    log_info(
        f"[Dashboard] mode={mode} summary={summary} filter={filter_status or 'none'}"
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

    categories = group_quests_by_category(
        legacy_steps if mode in {"legacy", "all"} else [],
        themepark_quests if mode in {"themepark", "all"} else [],
    )

    step_groups = group_steps_by_category(
        legacy_steps if mode in {"legacy", "all"} else [],
        themepark_quests if mode in {"themepark", "all"} else [],
    )

    for cat, steps in step_groups.items():
        status_list = categories.get(cat, [])
        counts = summarize_status_counts(status_list)
        log_info(f"[Dashboard] {cat} counts={counts} steps={len(steps)}")
        summary_line = " ".join(
            f"{emoji}{count}" for emoji, count in counts.items() if count
        )
        percent = calculate_completion_percentage(counts)
        Console().print(f"{cat}: {summary_line} ({percent:.0f}% complete)")
        if summary:
            continue
        if cat == "Theme Parks":
            Console().print(render_themepark_table(steps))
        else:
            Console().print(render_legacy_table(steps, summary=False))

    if summary:
        Console().print(build_summary_table(categories))


__all__ = ["show_unified_dashboard"]
