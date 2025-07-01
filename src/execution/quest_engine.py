"""Compatibility wrapper for legacy ``quest_engine`` module.

This module previously implemented ``execute_quest_step`` directly. It now
forwards calls to :func:`src.engine.quest_executor.run_step_with_feedback` and
emits a deprecation warning.
"""
from __future__ import annotations

from warnings import warn

from src.engine.quest_executor import run_step_with_feedback

warn(
    "src.execution.quest_engine is deprecated; use src.engine.quest_executor instead",
    DeprecationWarning,
    stacklevel=2,
)

execute_quest_step = run_step_with_feedback

__all__ = ["execute_quest_step"]
