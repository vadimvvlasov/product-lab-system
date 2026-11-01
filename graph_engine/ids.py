"""Filesystem-safe identifier rules shared by persistence boundaries."""

import re

SAFE_ID_PATTERN = re.compile(r"^[a-zA-Z0-9_-]+$")


def is_safe_id(value: object) -> bool:
    """Return True when value is a non-empty filesystem-safe identifier."""
    return isinstance(value, str) and bool(SAFE_ID_PATTERN.match(value))


def require_safe_id(value: object, kind: str = "id") -> str:
    """Return value or raise ValueError when it is not filesystem-safe."""
    if not is_safe_id(value):
        raise ValueError(
            f"Invalid {kind} {value!r}: only letters, digits, underscore and dash are allowed"
        )
    return value  # type: ignore[return-value]
