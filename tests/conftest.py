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

sys.modules.setdefault('cv2', types.SimpleNamespace(COLOR_RGB2BGR=None, cvtColor=lambda img, flag: img))

if 'numpy' not in sys.modules:
    np_module = types.ModuleType('numpy')
    np_module.array = lambda x: x
    np_module.ndarray = object
    sys.modules['numpy'] = np_module

sys.modules.setdefault('pyautogui', types.SimpleNamespace(screenshot=lambda *a, **k: sys.modules['PIL.Image'].new('RGB', (1, 1))))
