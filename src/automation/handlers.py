import pyautogui
import time


def press_continue():
    print("[ACTION] Pressing 'Continue'")
    pyautogui.press("enter")


def click_confirm():
    print("[ACTION] Clicking center for confirm")
    pyautogui.click(x=960, y=540)  # Adjust if needed


def handle_npc_dialogue():
    print("[ACTION] Handling NPC Dialogue")
    pyautogui.press("1")  # Assume '1' selects dialogue option
    time.sleep(0.5)
    pyautogui.press("enter")
