"""Grammar for `env:NAME` references in executor config values.

Shared by workflow validation and the config snapshot so the two cannot drift.
"""

import re

ENV_PREFIX = "env:"

# ASCII classes spelled out on purpose: \w and \d would match unicode.
ENV_NAME = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
ENV_NAME_GRAMMAR = "[A-Za-z_][A-Za-z0-9_]*"


def is_env_ref(value: object) -> bool:
    """Return True when value is a string that starts with the `env:` marker."""
    return isinstance(value, str) and value.startswith(ENV_PREFIX)


def env_ref_error(value: object) -> str | None:
    """Return an error message when value is a malformed `env:` reference.

    Returns None for valid references and for values that are not references
    (non-strings and strings that do not start with the case-sensitive `env:`
    prefix). The name is never trimmed: whitespace is a rejection.
    """
    if not is_env_ref(value):
        return None
    name = value[len(ENV_PREFIX):]
    if ENV_NAME.fullmatch(name):
        return None
    if not name.strip():
        return (
            f"environment variable name is empty in {value!r}; "
            f"expected env:NAME with NAME matching {ENV_NAME_GRAMMAR}"
        )
    return (
        f"invalid environment variable name {name!r} in {value!r}; "
        f"expected {ENV_NAME_GRAMMAR}"
    )
