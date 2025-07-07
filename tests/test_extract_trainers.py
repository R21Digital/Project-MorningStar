

from scripts.data import extract_trainers


def test_extract_trainers_writes_yaml(monkeypatch, tmp_path):
    samples = tmp_path / "samples"
    samples.mkdir()
    (samples / "trainer.png").write_bytes(b"fake")

    out_file = tmp_path / "trainers.yaml"

    monkeypatch.setattr(extract_trainers, "SAMPLES_DIR", samples)
    monkeypatch.setattr(extract_trainers, "OUT_FILE", out_file)

    monkeypatch.setattr(extract_trainers.cv2, "imread", lambda p: "img", raising=False)

    text = (
        "profession: artisan\n"
        "planet: tatooine\n"
        "city: mos_eisley\n"
        "name: Sample Trainer\n"
        "x: 1\n"
        "y: 2"
    )
    monkeypatch.setattr(extract_trainers, "extract_text", lambda img: text)

    monkeypatch.setattr(extract_trainers.yaml, "safe_load", lambda s: {})
    monkeypatch.setattr(
        extract_trainers.yaml,
        "safe_dump",
        lambda d, fh: fh.write(str(d)),
        raising=False,
    )

    extract_trainers.main()

    assert out_file.exists()
    content = out_file.read_text()
    assert "Sample Trainer" in content
    assert "artisan" in content
