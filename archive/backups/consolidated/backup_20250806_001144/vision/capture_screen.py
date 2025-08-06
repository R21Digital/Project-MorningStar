import pyautogui

def capture_screen(region=None):
    """Return a screenshot of the region as a ``PIL.Image``."""
    screenshot = pyautogui.screenshot(region=region)
    return screenshot
