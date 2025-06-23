"""Convenience imports for database helpers."""

from .database import get_connection, get_db, DB_PATH
from .models import create_schema
from .queries import (
    insert_quest,
    select_best_quest,
    insert_note,
    get_notes,
)

__all__ = [
    "get_connection",
    "get_db",
    "DB_PATH",
    "create_schema",
    "insert_quest",
    "select_best_quest",
    "insert_note",
    "get_notes",
]
