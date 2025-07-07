
from core.shuttle_travel import get_shuttle_path


def test_get_shuttle_path_returns_direct_route():
    assert get_shuttle_path("a", "b") == ["a", "b"]
