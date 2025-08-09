"""Test environment initialization importing optional dependencies."""

# Ensure BeautifulSoup is available for tests that rely on it.
try:
    import bs4  # noqa: F401
except Exception:
    pass

"""
Provide a very small fallback implementation for ``rich`` so tests don't fail
when the optional dependency isn't installed in the execution environment.

Important: Avoid importing from the repository's ``tests`` package here because
pytest may import ``tests`` from archived backups first, causing
ImportPathMismatch. We inline a minimal stub instead.
"""
try:
    import rich  # type: ignore
except Exception:
    import sys as _sys
    import types as _types

    _rich = _types.ModuleType("rich")

    class _Console:  # minimal console
        printed: list[str] = []

        def print(self, *args, **kwargs):
            rendered = " ".join(str(a) for a in args)
            self.printed.append(rendered)
            print(rendered)

    console = _types.ModuleType("console")
    console.Console = _Console
    _rich.console = console

    class _Table:
        def __init__(self, *args, **kwargs):
            self.rows = []
            self.columns = []
            self.title = kwargs.get("title", "")

        def add_column(self, name, *args, **kwargs):
            self.columns.append(name)

        def add_row(self, *args, **kwargs):
            self.rows.append(args)

        def __str__(self) -> str:
            rows = [" | ".join(str(c) for c in r) for r in self.rows]
            header = " | ".join(self.columns)
            parts = []
            if self.title:
                parts.append(self.title)
            if header:
                parts.append(header)
            if rows:
                parts.append("\n".join(rows))
            return "\n".join(parts)

    table = _types.ModuleType("table")
    table.Table = _Table
    _rich.table = table

    class _Layout:
        def __init__(self, *args, **kwargs):
            self.children = list(args)

        def split_column(self, *layouts):
            self.children.extend(layouts)

        def __str__(self) -> str:
            return "\n".join(str(c) for c in self.children)

    layout = _types.ModuleType("layout")
    layout.Layout = _Layout
    _rich.layout = layout

    _sys.modules.setdefault("rich", _rich)
    _sys.modules.setdefault("rich.console", console)
    _sys.modules.setdefault("rich.table", table)
    _sys.modules.setdefault("rich.layout", layout)

# Remove archived backup directories from sys.path to avoid duplicate module names
# (e.g., another top-level "tests" package inside archived backups causing
# ImportPathMismatch in pytest on Windows.)
try:
    import os
    import sys as _sys

    _repo_root = os.path.dirname(__file__)
    _archive_dir = os.path.join(_repo_root, "archive")

    for _p in list(_sys.path):
        try:
            _norm = os.path.normpath(_p)
        except Exception:
            continue
        if _norm.startswith(os.path.normpath(_archive_dir)):
            try:
                _sys.path.remove(_p)
            except ValueError:
                pass
except Exception:
    # Best-effort only; never fail test environment initialization
    pass