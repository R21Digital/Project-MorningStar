import os
import sys
from PIL import Image


from core.trainer_scanner import scan_trainer_skills
import pyautogui
import cv2
import pytesseract


def test_scan_trainer_skills(monkeypatch):
    test_img = Image.new("RGB", (10, 10), color="white")

    monkeypatch.setattr(pyautogui, "screenshot", lambda region=None: test_img)
    monkeypatch.setattr(cv2, "cvtColor", lambda img, flag: img)
    monkeypatch.setattr(cv2, "threshold", lambda img, *a, **k: (None, img), raising=False)
    monkeypatch.setattr(pytesseract, "image_to_string", lambda img: "Skill A\nSkill B")

    skills = scan_trainer_skills()
    assert skills == ["Skill A", "Skill B"]
