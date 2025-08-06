

from core import trainer_ocr


def test_get_untrained_skills_from_text():
    sample = """\
Train Novice Artisan
Train Novice Marksman
Already trained something
XP cost 100
Some: thing
Train Master Swordsman
"""
    result = trainer_ocr.get_untrained_skills_from_text(sample)
    assert result == [
        "Train Novice Artisan",
        "Train Novice Marksman",
        "Train Master Swordsman",
    ]


def test_scan_and_detect_untrained_skills(monkeypatch):
    ocr_text = "Train Novice Artisan\nXP cost 50\nTrain Novice Marksman\n"
    monkeypatch.setattr(trainer_ocr, "capture_screen_region", lambda region=None: object())
    monkeypatch.setattr(trainer_ocr, "preprocess_image", lambda img: img)
    monkeypatch.setattr(trainer_ocr.pytesseract, "image_to_string", lambda img: ocr_text)

    skills = trainer_ocr.scan_and_detect_untrained_skills()
    assert skills == ["Train Novice Artisan", "Train Novice Marksman"]
