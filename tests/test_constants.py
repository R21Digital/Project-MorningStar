import importlib.util
import sys
import types
from pathlib import Path

# Preload ``core.constants`` without importing ``core.__init__``
_constants_path = Path(__file__).resolve().parents[1] / "core" / "constants.py"
_spec = importlib.util.spec_from_file_location("core.constants", _constants_path)
_constants = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_constants)  # type: ignore[attr-defined]

_core_pkg = types.ModuleType("core")
_core_pkg.__path__ = []
_core_pkg.constants = _constants
sys.modules["core"] = _core_pkg
sys.modules["core.constants"] = _constants

from core.constants import (
    STATUS_COMPLETED,
    STATUS_FAILED,
    STATUS_IN_PROGRESS,
    STATUS_UNKNOWN,
)

# Clean up our temporary stubs so other tests use the real package
sys.modules.pop("core.constants", None)
sys.modules.pop("core", None)


def test_constants_values():
    assert STATUS_COMPLETED == "✅ Completed"
    assert STATUS_FAILED == "❌ Failed"
    assert STATUS_IN_PROGRESS == "⏳ In Progress"
    assert STATUS_UNKNOWN == "❓ Unknown"

