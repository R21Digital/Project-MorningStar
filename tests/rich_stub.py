import sys
import types


def register_rich_stub():
    """Install minimal ``rich`` replacements for test environments."""
    _rich = types.ModuleType("rich")

    class _Console:
        """Very small stub of :class:`rich.console.Console`."""

        printed: list[str] = []

        def print(self, *args, **kwargs):
            rendered = " ".join(str(a) for a in args)
            self.printed.append(rendered)
            print(rendered)

    console = types.ModuleType("console")
    console.Console = _Console
    _rich.console = console

    class _Table:
        """Minimal ``Table`` implementation for tests."""

        def __init__(self, *args, **kwargs):
            self.rows = []
            self.columns = []
            self.title = kwargs.get("title", "")

        def add_column(self, name, *args, **kwargs):
            self.columns.append(name)

        def add_row(self, *args, **kwargs):
            self.rows.append(args)

        def __str__(self) -> str:  # pragma: no cover - trivial
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

    table = types.ModuleType("table")
    table.Table = _Table
    _rich.table = table

    class _Layout:
        def __init__(self, *args, **kwargs):
            self.children = list(args)

        def split_column(self, *layouts):
            self.children.extend(layouts)

        def __str__(self) -> str:  # pragma: no cover - trivial
            return "\n".join(str(c) for c in self.children)

    layout = types.ModuleType("layout")
    layout.Layout = _Layout
    _rich.layout = layout

    sys.modules.setdefault("rich", _rich)
    sys.modules.setdefault("rich.console", console)
    sys.modules.setdefault("rich.table", table)
    sys.modules.setdefault("rich.layout", layout)
