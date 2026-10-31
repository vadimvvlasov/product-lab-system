"""Tests for command verification."""

import pytest

from graph_engine.verification.base import (
    VerificationCriterion,
    VerificationMethod,
    VerificationStatus,
)
from graph_engine.verification.command import CommandVerifier


@pytest.fixture
def temp_staging(tmp_path):
    """Create temporary staging directory."""
    staging = tmp_path / "staging"
    staging.mkdir()
    # Create a test file
    (staging / "test.txt").write_text("hello")
    return staging


def test_command_pass(temp_staging):
    """Test passing command verification."""
    verifier = CommandVerifier()

    criterion = VerificationCriterion(
        id="file_exists",
        method=VerificationMethod.COMMAND,
        command="test -f test.txt",
    )

    result = verifier.verify(criterion, temp_staging, {})

    assert result.criterion_id == "file_exists"
    assert result.status == VerificationStatus.PASS
    assert result.exit_code == 0
    assert result.duration_seconds is not None


def test_command_fail(temp_staging):
    """Test failing command verification."""
    verifier = CommandVerifier()

    criterion = VerificationCriterion(
        id="file_missing",
        method=VerificationMethod.COMMAND,
        command="test -f missing.txt",
    )

    result = verifier.verify(criterion, temp_staging, {})

    assert result.criterion_id == "file_missing"
    assert result.status == VerificationStatus.FAIL
    assert result.exit_code == 1


def test_command_not_found(temp_staging):
    """Test command not found error."""
    verifier = CommandVerifier()

    criterion = VerificationCriterion(
        id="bad_command",
        method=VerificationMethod.COMMAND,
        command="nonexistent_command_xyz",
    )

    result = verifier.verify(criterion, temp_staging, {})

    assert result.criterion_id == "bad_command"
    assert result.status == VerificationStatus.ERROR
    assert "not found" in result.message.lower()


def test_command_timeout(temp_staging):
    """Test command timeout."""
    verifier = CommandVerifier()

    criterion = VerificationCriterion(
        id="slow_command",
        method=VerificationMethod.COMMAND,
        command="sleep 10",
        timeout_seconds=1,
    )

    result = verifier.verify(criterion, temp_staging, {})

    assert result.criterion_id == "slow_command"
    assert result.status == VerificationStatus.ERROR
    assert "timed out" in result.message.lower()


def test_command_captures_stdout_stderr(temp_staging):
    """Test stdout/stderr capture using a simple script."""
    verifier = CommandVerifier()

    # Create a test script
    script = temp_staging / "test_script.sh"
    script.write_text("#!/bin/sh\necho hello\necho error >&2\n")
    script.chmod(0o755)

    criterion = VerificationCriterion(
        id="output_test",
        method=VerificationMethod.COMMAND,
        command=str(script),
    )

    result = verifier.verify(criterion, temp_staging, {})

    assert result.status == VerificationStatus.PASS
    assert "hello" in result.stdout
    assert "error" in result.stderr


def test_command_shell_metacharacters_rejected(temp_staging):
    """Test that shell metacharacters are rejected in MVP."""
    verifier = CommandVerifier()

    dangerous_commands = [
        "ls | grep test",
        "echo test > output.txt",
        "cmd1 && cmd2",
        "cmd1 || cmd2",
        "cmd1; cmd2",
    ]

    for cmd in dangerous_commands:
        criterion = VerificationCriterion(
            id="dangerous",
            method=VerificationMethod.COMMAND,
            command=cmd,
        )

        result = verifier.verify(criterion, temp_staging, {})

        assert result.status == VerificationStatus.ERROR
        assert "metacharacters not allowed" in result.message


def test_command_missing_command_field(temp_staging):
    """Test missing command field."""
    verifier = CommandVerifier()

    criterion = VerificationCriterion(
        id="missing_cmd",
        method=VerificationMethod.COMMAND,
        command=None,
    )

    result = verifier.verify(criterion, temp_staging, {})

    assert result.status == VerificationStatus.ERROR
    assert "missing 'command'" in result.message.lower()


def test_command_empty_after_parsing(temp_staging):
    """Test empty command after parsing."""
    verifier = CommandVerifier()

    criterion = VerificationCriterion(
        id="empty",
        method=VerificationMethod.COMMAND,
        command="   ",  # Only whitespace
    )

    result = verifier.verify(criterion, temp_staging, {})

    assert result.status == VerificationStatus.ERROR
    assert "empty" in result.message.lower()


def test_command_output_truncation(temp_staging):
    """Test that large output is truncated."""
    verifier = CommandVerifier(max_output_bytes=100)

    # Generate large output using perl (available in /usr/bin)
    criterion = VerificationCriterion(
        id="large_output",
        method=VerificationMethod.COMMAND,
        command='/usr/bin/perl -e "print q{x} x 200"',
    )

    result = verifier.verify(criterion, temp_staging, {})

    assert result.status == VerificationStatus.PASS
    assert len(result.stdout) <= 150  # Truncated + message
    assert "truncated" in result.stdout.lower()
