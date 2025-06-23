import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.source_verifier import file_changed, verify_source


def test_file_changed_detects_modifications(tmp_path):
    html_path = tmp_path / "legacy.html"
    hash_path = tmp_path / "legacy.hash"

    html_path.write_text("first")
    assert file_changed(html_path, hash_path) is True

    # No change should return False
    assert file_changed(html_path, hash_path) is False

    # Modify file and ensure change is detected
    html_path.write_text("second")
    assert file_changed(html_path, hash_path) is True


def test_verify_source_basic_validation():
    assert verify_source({"title": "Quest", "steps": []}) is True
    assert verify_source({"steps": []}) is False
    assert verify_source("oops") is False
