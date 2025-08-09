"""MS11 helper library (SWG-focused stubs)

This package provides thin wrappers and utilities for:
 - window: attach/find SWG window, focus checks
 - ocr: basic text capture helpers
 - shortcuts: register/validate local keybinds
 - events: simple pub/sub in-process bus
 - nav: placeholders for navigation mesh/path queries

Implementations here are intentionally lightweight and safe to import
on machines without extra deps. Each module guards OS-specific imports.
"""

from . import window, ocr, shortcuts, events, nav  # re-export modules

__all__ = [
    "window",
    "ocr",
    "shortcuts",
    "events",
    "nav",
]


