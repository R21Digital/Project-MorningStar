import sys
import types


def register_rich_stub():
    """Install minimal ``rich`` replacements for test environments."""
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

        def add_column(self, *args, **kwargs):
            pass

        def add_row(self, *args, **kwargs):
            self.rows.append(args)

        def __str__(self) -> str:  # pragma: no cover - trivial
            return "\n".join(" | ".join(str(c) for c in r) for r in self.rows)

    table = types.ModuleType("table")
    table.Table = _Table
    _rich.table = table

    class _Layout:
        def __init__(self, *args, **kwargs):
            self.children = []

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
