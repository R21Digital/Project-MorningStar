"""Helpers for executing quest steps."""

from .core import execute_step

__all__ = ["execute_step", "StateManager"]


def __getattr__(name: str):
    if name == "StateManager":
        from .state_manager import StateManager as _StateManager
        return _StateManager
    raise AttributeError(name)
