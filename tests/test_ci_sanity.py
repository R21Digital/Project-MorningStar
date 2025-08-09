"""Sanity tests for CI pipeline to ensure basic functionality works."""

import pytest
from pathlib import Path


def test_project_structure():
    """Test that basic project structure exists."""
    assert Path("src").exists(), "src directory should exist"
    assert Path("tests").exists(), "tests directory should exist"
    assert Path("requirements.txt").exists(), "requirements.txt should exist"


def test_core_imports():
    """Test that core modules can be imported."""
    try:
        from core.session_manager import SessionData
        assert SessionData is not None
    except ImportError as e:
        # Fallback to public schema if private core isn't available locally
        try:
            from swgdb_api.schemas.session_v1 import SessionData  # type: ignore

            assert SessionData is not None
        except Exception as inner:
            pytest.fail(f"Failed to import SessionData: {e}; fallback also failed: {inner}")


def test_basic_math():
    """Simple math test to ensure pytest is working."""
    assert 2 + 2 == 4
    assert 3 * 3 == 9


def test_string_operations():
    """Test basic string operations."""
    test_string = "hello world"
    assert test_string.upper() == "HELLO WORLD"
    assert len(test_string) == 11


if __name__ == "__main__":
    pytest.main([__file__])
