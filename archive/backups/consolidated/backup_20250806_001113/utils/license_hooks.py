"""Decorators for optional license checks."""

from __future__ import annotations

from functools import wraps
import os
import warnings


def requires_license(func):
    """Warn if the application is run without a license key.

    The decorator checks for ``ANDROID_MS11_LICENSE`` in the environment and
    emits a :class:`RuntimeWarning` when it is missing. This placeholder will be
    replaced by a real license validation routine in the future.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        if os.environ.get("ANDROID_MS11_LICENSE") is None:
            warnings.warn(
                "License check is not implemented yet. Running in trial mode.",
                RuntimeWarning,
            )
        return func(*args, **kwargs)

    return wrapper


__all__ = ["requires_license"]
