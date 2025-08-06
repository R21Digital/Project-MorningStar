"""
Platform-specific utilities for testing.

This module provides utilities to handle platform differences in tests,
particularly for Windows-specific functionality that doesn't work on Linux.
"""

import sys
import pytest
from unittest.mock import Mock, patch
from typing import Optional, Callable, Any


def skip_on_linux(reason: str = "Test not supported on Linux"):
    """Decorator to skip tests on Linux."""
    return pytest.mark.skipif(
        sys.platform.startswith("linux"),
        reason=reason
    )


def skip_on_windows(reason: str = "Test not supported on Windows"):
    """Decorator to skip tests on Windows."""
    return pytest.mark.skipif(
        sys.platform.startswith("win"),
        reason=reason
    )


def windows_only(reason: str = "Test requires Windows"):
    """Decorator to run tests only on Windows."""
    return pytest.mark.skipif(
        not sys.platform.startswith("win"),
        reason=reason
    )


def linux_only(reason: str = "Test requires Linux"):
    """Decorator to run tests only on Linux."""
    return pytest.mark.skipif(
        not sys.platform.startswith("linux"),
        reason=reason
    )


def mock_windows_dependencies(func: Callable) -> Callable:
    """Decorator to mock Windows-specific dependencies."""
    def wrapper(*args, **kwargs):
        if not sys.platform.startswith("win"):
            with patch.dict('sys.modules', {
                'win32api': Mock(),
                'win32gui': Mock(),
                'win32con': Mock(),
                'win32process': Mock(),
                'pygetwindow': Mock(),
                'pyautogui': Mock(),
            }):
                return func(*args, **kwargs)
        else:
            return func(*args, **kwargs)
    return wrapper


def mock_pygetwindow(func: Callable) -> Callable:
    """Decorator to mock PyGetWindow for Linux compatibility."""
    def wrapper(*args, **kwargs):
        if sys.platform.startswith("linux"):
            with patch.dict('sys.modules', {
                'pygetwindow': Mock(),
                'pyautogui': Mock(),
            }):
                return func(*args, **kwargs)
        else:
            return func(*args, **kwargs)
    return wrapper


def handle_system_exit(func: Callable) -> Callable:
    """Decorator to handle SystemExit exceptions in tests."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except SystemExit as e:
            # Convert SystemExit to a test failure
            pytest.fail(f"Test called sys.exit({e.code})")
    return wrapper


def is_windows() -> bool:
    """Check if running on Windows."""
    return sys.platform.startswith("win")


def is_linux() -> bool:
    """Check if running on Linux."""
    return sys.platform.startswith("linux")


def is_macos() -> bool:
    """Check if running on macOS."""
    return sys.platform.startswith("darwin")


def get_platform_name() -> str:
    """Get the current platform name."""
    if is_windows():
        return "windows"
    elif is_linux():
        return "linux"
    elif is_macos():
        return "macos"
    else:
        return "unknown"
