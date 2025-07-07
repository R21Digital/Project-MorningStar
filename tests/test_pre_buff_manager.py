

from android_ms11.core.pre_buff_manager import apply_pre_buffs


def test_apply_pre_buffs_prints_messages(capsys):
    apply_pre_buffs()
    captured = capsys.readouterr().out
    assert "Checking required buffs" in captured
    assert "Capturing screen for OCR" in captured
    assert "Casting Might" in captured
    assert "Pre-buff complete" in captured
