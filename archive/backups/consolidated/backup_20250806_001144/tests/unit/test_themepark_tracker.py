import importlib.util
from pathlib import Path
from core.constants import STATUS_EMOJI_MAP, STATUS_UNKNOWN

# Load the module directly to avoid running core.__init__
spec = importlib.util.spec_from_file_location(
    "core.themepark_tracker",
    Path(__file__).resolve().parents[1] / "core" / "themepark_tracker.py",
)
themepark_tracker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(themepark_tracker)


def test_get_themepark_status(monkeypatch):
    logs = [
        "Imperial Museum Completed",
        "Rebel Adventure In Progress",
        "Science Quest Failed",
    ]
    monkeypatch.setattr(themepark_tracker, "read_themepark_log", lambda: logs)

    assert themepark_tracker.get_themepark_status("Imperial Museum") == STATUS_EMOJI_MAP["completed"]
    assert themepark_tracker.get_themepark_status("Rebel Adventure") == STATUS_EMOJI_MAP["in_progress"]
    assert themepark_tracker.get_themepark_status("Science Quest") == STATUS_EMOJI_MAP["failed"]
    assert themepark_tracker.get_themepark_status("Unknown Quest") == STATUS_UNKNOWN


def test_is_themepark_quest_active(monkeypatch):
    logs = [
        "Imperial Museum Completed",
        "Rebel Adventure In Progress",
        "Science Quest Failed",
    ]
    monkeypatch.setattr(themepark_tracker, "read_themepark_log", lambda: logs)

    assert themepark_tracker.is_themepark_quest_active("imperial museum") is True
    assert themepark_tracker.is_themepark_quest_active("REBEL adventure") is True
    assert themepark_tracker.is_themepark_quest_active("Science Quest") is True
    assert themepark_tracker.is_themepark_quest_active("Unknown Quest") is False
