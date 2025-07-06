"""Test environment initialization importing optional dependencies."""

# Ensure BeautifulSoup is available for tests that rely on it.
try:
    import bs4  # noqa: F401
except Exception:
    pass

# Provide a very small fallback implementation for ``rich`` so tests don't fail
# when the optional dependency isn't installed in the execution environment.
try:
    import rich  # noqa: F401
except Exception:
    import sys
    import types

    _rich = types.ModuleType("rich")

    class _Console:
        def print(self, *args, **kwargs):
            print(*args)

    console = types.ModuleType("console")
    console.Console = _Console
    _rich.console = console

    class _Table:
        def __init__(self, *args, **kwargs):
            self.rows = []
            self.title = kwargs.get('title')

        def add_column(self, *args, **kwargs):
            pass

        def add_row(self, *args, **kwargs):
            self.rows.append(args)

        def __str__(self) -> str:  # pragma: no cover - trivial
            lines = []
            if self.title:
                lines.append(self.title)
            lines.extend(" | ".join(str(c) for c in r) for r in self.rows)
            return "\n".join(lines)

    table = types.ModuleType("table")
    table.Table = _Table
    _rich.table = table

    class _Layout:
        def __init__(self, content=None, *args, **kwargs):
            self.content = content
            self.children = []

        def split_column(self, *layouts):
            self.children.extend(layouts)

        def __str__(self) -> str:  # pragma: no cover - trivial
            if self.children:
                return "\n".join(str(c) for c in self.children)
            if self.content is not None:
                return str(self.content)
            return ""

    layout = types.ModuleType("layout")
    layout.Layout = _Layout
    _rich.layout = layout

    sys.modules.setdefault("rich", _rich)
    sys.modules.setdefault("rich.console", console)
    sys.modules.setdefault("rich.table", table)
    sys.modules.setdefault("rich.layout", layout)
