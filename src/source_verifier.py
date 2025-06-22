"""Simple quest source verification utilities."""

from typing import Any


def verify_source(data: Any) -> bool:
    """Return ``True`` if ``data`` appears trustworthy."""
    print(f"[DEBUG] Verifying quest source: {data}")
    # TODO: implement real signature or hash checks
    return True
