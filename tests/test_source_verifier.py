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


def test_verify_source_with_string():
    assert verify_source("trusted_data") is True
    assert verify_source("untrusted") is False


def test_verify_source_with_file(tmp_path):
    p = tmp_path / "data.txt"
    p.write_text("trusted_data")
    assert verify_source(p) is True
    p.write_text("evil")
    assert verify_source(p) is False
