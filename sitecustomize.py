"""Test environment initialization importing optional dependencies."""

# Ensure BeautifulSoup is available for tests that rely on it.
try:
    import bs4  # noqa: F401
except Exception:
    pass
