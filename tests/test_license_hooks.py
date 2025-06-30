import os
import warnings
import sys


from utils.license_hooks import requires_license


def test_requires_license_warns(monkeypatch):
    monkeypatch.delenv("ANDROID_MS11_LICENSE", raising=False)

    @requires_license
    def sample_fn():
        return 1

    with warnings.catch_warnings(record=True) as rec:
        warnings.simplefilter("always")
        assert sample_fn() == 1
        assert any("License check is not implemented" in str(w.message) for w in rec)
