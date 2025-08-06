"""Test environment initialization importing optional dependencies."""

# Ensure BeautifulSoup is available for tests that rely on it.
try:
    import bs4  # noqa: F401
except Exception:
    pass

# Provide a very small fallback implementation for ``rich`` so tests don't fail
# when the optional dependency isn't installed in the execution environment.
try:
    import rich  # noqa: F401
except Exception:
    from tests.rich_stub import register_rich_stub

    register_rich_stub()
