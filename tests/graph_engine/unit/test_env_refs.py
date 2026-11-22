"""Tests for the shared env:NAME reference grammar."""

import pytest

from graph_engine.env_refs import ENV_NAME, env_ref_error

ACCEPTED = [
    "env:OPENAI_API_KEY", "env:DB_PWD", "env:_X", "env:a1", "env:A", "env:_",
]
REJECTED = [
    "env:", "env: ", "env:   ", "env:FOO BAR", "env: DB_PWD", "env:DB_PWD ",
    "env:DB_PWD\n", "env:A=B", "env:$HOME", "env:${HOME}", "env:a/b", "env:a\\b",
    "env:A-B", "env:1X", "env:ПАРОЛЬ", "env:Pässword", "env:A.B",
]


@pytest.mark.parametrize("value", ACCEPTED)
def test_valid_names_accepted(value):
    assert env_ref_error(value) is None


@pytest.mark.parametrize("value", REJECTED)
def test_invalid_names_rejected(value):
    error = env_ref_error(value)
    assert error is not None
    assert "env:NAME" in error or "invalid environment variable name" in error
    assert "[A-Za-z_][A-Za-z0-9_]*" in error


def test_trailing_newline_is_visible_in_message():
    assert "\\n" in env_ref_error("env:DB_PWD\n")


@pytest.mark.parametrize("value", ["https://x", "ENV:x", "prod", "", "xenv:A"])
def test_non_reference_values_are_not_checked(value):
    assert env_ref_error(value) is None


def test_grammar_is_ascii_only():
    assert ENV_NAME.pattern == r"[A-Za-z_][A-Za-z0-9_]*"
