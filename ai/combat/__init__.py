"""Compat module exposing combat AI runtime from ``src.ai``."""

from src.ai.combat import *  # re-export everything for backwards compatibility

__all__ = ["evaluate_state", "CombatRunner"]
