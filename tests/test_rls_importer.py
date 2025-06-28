from android_ms11.data_importers.rls_importer import load_rls_mobs


def test_load_rls_mobs_returns_list(tmp_path):
    sample = tmp_path / "sample.json"
    sample.write_text('[{"name": "Test", "planet": "corellia"}]')
    result = load_rls_mobs(sample)
    assert isinstance(result, list)
    assert result[0]["name"] == "Test"
