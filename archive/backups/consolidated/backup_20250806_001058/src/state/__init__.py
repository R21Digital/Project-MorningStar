"""Game state helpers."""

__all__ = ["StateManager"]


def __getattr__(name: str):
    if name == "StateManager":
        from .state_manager import StateManager as _StateManager
        return _StateManager
    raise AttributeError(name)
