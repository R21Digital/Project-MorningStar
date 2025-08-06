import importlib.util
import importlib
import sys
import types
from pathlib import Path

# Preload ``core.constants`` without importing ``core.__init__``
_constants_path = Path(__file__).resolve().parents[1] / "core" / "constants.py"
_spec = importlib.util.spec_from_file_location("core.constants", _constants_path)
_constants = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_constants)  # type: ignore[attr-defined]

_prev_core = sys.modules.get("core")
_prev_constants = sys.modules.get("core.constants")

_core_pkg = types.ModuleType("core")
_core_pkg.__path__ = []
_core_pkg.constants = _constants
sys.modules["core"] = _core_pkg
sys.modules["core.constants"] = _constants

constants = importlib.import_module("core.constants")
STATUS_COMPLETED = constants.STATUS_COMPLETED
STATUS_FAILED = constants.STATUS_FAILED
STATUS_IN_PROGRESS = constants.STATUS_IN_PROGRESS
STATUS_NOT_STARTED = constants.STATUS_NOT_STARTED
STATUS_UNKNOWN = constants.STATUS_UNKNOWN
STATUS_EMOJI_MAP = constants.STATUS_EMOJI_MAP
STATUS_NAME_FROM_EMOJI = constants.STATUS_NAME_FROM_EMOJI
VALID_STATUS_EMOJIS = constants.VALID_STATUS_EMOJIS
__all__ = constants.__all__

# Clean up our temporary stubs so other tests use the real package
if _prev_constants is not None:
    sys.modules["core.constants"] = _prev_constants
else:
    sys.modules.pop("core.constants", None)

if _prev_core is not None:
    sys.modules["core"] = _prev_core
else:
    sys.modules.pop("core", None)


def test_constants_values():
    assert STATUS_COMPLETED == "✅"
    assert STATUS_FAILED == "❌"
    assert STATUS_IN_PROGRESS == "⏳"
    assert STATUS_NOT_STARTED == "🕒"
    assert STATUS_UNKNOWN == "❓"
    for name in (
        "STATUS_COMPLETED",
        "STATUS_FAILED",
        "STATUS_IN_PROGRESS",
        "STATUS_NOT_STARTED",
        "STATUS_UNKNOWN",
        "STATUS_EMOJI_MAP",
        "STATUS_NAME_FROM_EMOJI",
        "VALID_STATUS_EMOJIS",
    ):
        assert name in __all__

    expected_map = {
        "completed": STATUS_COMPLETED,
        "failed": STATUS_FAILED,
        "in_progress": STATUS_IN_PROGRESS,
        "not_started": STATUS_NOT_STARTED,
    }
    assert STATUS_EMOJI_MAP == expected_map
    assert STATUS_NAME_FROM_EMOJI == {v: k for k, v in expected_map.items()}
    assert VALID_STATUS_EMOJIS == set(expected_map.values())

