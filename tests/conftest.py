import sys
import types

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

from pathlib import Path
import pytest


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
