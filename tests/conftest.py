import os
import sys
import types
from pathlib import Path
import pytest
from unittest.mock import Mock, patch

try:
    import rich  # noqa: F401
except Exception:
    from .rich_stub import register_rich_stub

    register_rich_stub()

# Ensure project root is on the import path for tests
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# Also include the project's ``src`` directory so ``ai`` and other packages
# resolve the same way they do in production installs.
SRC_ROOT = os.path.join(ROOT, "src")
if SRC_ROOT not in sys.path:
    # Prepend to ensure it takes precedence over any top-level packages
    sys.path.insert(0, SRC_ROOT)

# Ensure the top-level ``ai`` package resolves during tests
AI_ROOT = os.path.join(ROOT, "ai")
if AI_ROOT not in sys.path:
    sys.path.insert(0, AI_ROOT)

# Provide stub modules for optional dependencies
if 'pytesseract' not in sys.modules:
    sys.modules['pytesseract'] = types.SimpleNamespace(image_to_string=lambda *a, **k: '')

if 'PIL' not in sys.modules:
    pil_module = types.ModuleType('PIL')
    pil_image = types.SimpleNamespace(new=lambda *a, **k: object())
    pil_module.Image = pil_image
    sys.modules['PIL'] = pil_module
    sys.modules['PIL.Image'] = pil_image

sys.modules.setdefault(
    'cv2',
    types.SimpleNamespace(
        COLOR_RGB2BGR=None,
        COLOR_BGR2GRAY=None,
        THRESH_BINARY=None,
        cvtColor=lambda img, flag: img,
        threshold=lambda img, *a, **k: (None, img),
    ),
)

if 'numpy' not in sys.modules:
    np_module = types.ModuleType('numpy')
    np_module.array = lambda x: x
    np_module.ndarray = object
    sys.modules['numpy'] = np_module

sys.modules.setdefault('pyautogui', types.SimpleNamespace(screenshot=lambda *a, **k: sys.modules['PIL.Image'].new('RGB', (1, 1))))

if 'yaml' not in sys.modules:
    yaml_module = types.ModuleType('yaml')
    def safe_load(stream):
        # Minimal trainer data for tests
        return {
            'artisan': {
                'tatooine': {
                    'mos_eisley': {
                        'name': 'Artisan Trainer',
                        'x': 3432,
                        'y': -4795,
                    }
                }
            }
        }
    yaml_module.safe_load = safe_load
    sys.modules['yaml'] = yaml_module



@pytest.fixture(autouse=True)
def trainer_file_env(monkeypatch):
    """Ensure tests load trainers from the project data directory."""
    default = (
        Path(__file__).resolve().parents[1]
        / "data"
        / "trainers.json"
    )
    monkeypatch.setenv("TRAINER_FILE", str(default))
    yield
    monkeypatch.delenv("TRAINER_FILE", raising=False)

# Platform-specific test configuration
def pytest_configure(config):
    """Configure pytest for platform-specific test skipping."""
    # Add custom markers
    config.addinivalue_line(
        "markers", "windows_only: mark test to run only on Windows"
    )
    config.addinivalue_line(
        "markers", "linux_skip: mark test to skip on Linux"
    )

def pytest_collection_modifyitems(config, items):
    """Modify test collection to skip platform-specific tests."""
    skip_windows_only = pytest.mark.skip(reason="Test requires Windows")
    skip_linux = pytest.mark.skip(reason="Test not supported on Linux")
    
    for item in items:
        # Skip Windows-only tests on non-Windows platforms
        if "windows_only" in item.keywords and not sys.platform.startswith("win"):
            item.add_marker(skip_windows_only)
        
        # Skip Linux-incompatible tests on Linux
        if "linux_skip" in item.keywords and sys.platform.startswith("linux"):
            item.add_marker(skip_linux)

@pytest.fixture(autouse=True)
def mock_pygetwindow():
    """Mock PyGetWindow for Linux compatibility."""
    if sys.platform.startswith("linux"):
        with patch.dict('sys.modules', {
            'pygetwindow': Mock(),
            'pyautogui': Mock(),
        }):
            yield
    else:
        yield

@pytest.fixture(autouse=True)
def mock_windows_dependencies():
    """Mock Windows-specific dependencies on non-Windows platforms."""
    if not sys.platform.startswith("win"):
        with patch.dict('sys.modules', {
            'win32api': Mock(),
            'win32gui': Mock(),
            'win32con': Mock(),
            'win32process': Mock(),
        }):
            yield
    else:
        yield
