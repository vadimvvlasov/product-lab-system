"""Tests for retry feedback builder."""

import pytest

from graph_engine.verification.base import VerificationResult, VerificationStatus
from graph_engine.verification.feedback import build_retry_feedback


def test_build_feedback_from_failed_verifications():
    """Test building feedback from failed verification results."""
    results = [
        VerificationResult(
            criterion_id="tests_pass",
            status=VerificationStatus.FAIL,
            message="Tests failed",
            stderr="AssertionError: expected 5, got 3",
        ),
        VerificationResult(
            criterion_id="lint",
            status=VerificationStatus.FAIL,
            message="Linting errors",
            stderr="unused import on line 42",
        ),
    ]
    
    feedback = build_retry_feedback(
        attempt_number=1,
        verification_results=results,
        missing_artifacts=[],
    )
    
    assert feedback.previous_attempt == 1
    assert len(feedback.failures) == 4  # 2 failures + 2 stderr entries
    assert "tests_pass: Tests failed" in feedback.failures
    assert "lint: Linting errors" in feedback.failures


def test_build_feedback_with_agent_findings():
    """Test feedback includes agent reviewer findings."""
    results = [
        VerificationResult(
            criterion_id="review",
            status=VerificationStatus.FAIL,
            message="Review found issues",
            findings=[
                "Missing error handling in parse_workflow",
                "Unchecked null pointer in line 15",
            ],
        ),
    ]
    
    feedback = build_retry_feedback(
        attempt_number=2,
        verification_results=results,
        missing_artifacts=[],
    )
    
    assert feedback.previous_attempt == 2
    assert feedback.reviewer_findings is not None
    assert "Missing error handling" in feedback.reviewer_findings
    assert "Unchecked null pointer" in feedback.reviewer_findings


def test_build_feedback_with_missing_artifacts():
    """Test feedback includes missing artifacts."""
    results = []
    
    feedback = build_retry_feedback(
        attempt_number=1,
        verification_results=results,
        missing_artifacts=["report.md", "metrics.json"],
    )
    
    assert feedback.missing_artifacts == ["report.md", "metrics.json"]


def test_build_feedback_with_verification_error():
    """Test feedback includes verification errors."""
    results = [
        VerificationResult(
            criterion_id="tests",
            status=VerificationStatus.ERROR,
            message="Command not found: pytest",
        ),
    ]
    
    feedback = build_retry_feedback(
        attempt_number=1,
        verification_results=results,
        missing_artifacts=[],
    )
    
    assert len(feedback.failures) == 1
    assert "ERROR" in feedback.failures[0]
    assert "Command not found" in feedback.failures[0]


def test_build_feedback_stderr_truncation():
    """Test that stderr is truncated in feedback."""
    long_stderr = "x" * 1000
    
    results = [
        VerificationResult(
            criterion_id="fail",
            status=VerificationStatus.FAIL,
            message="Failed",
            stderr=long_stderr,
        ),
    ]
    
    feedback = build_retry_feedback(
        attempt_number=1,
        verification_results=results,
        missing_artifacts=[],
    )
    
    # Find stderr entry
    stderr_entry = [f for f in feedback.failures if "stderr" in f][0]
    # Should be truncated to 500 chars
    assert len(stderr_entry) <= 510  # "  stderr: " prefix + 500 chars


def test_build_feedback_no_failures():
    """Test feedback when all passed (edge case)."""
    results = [
        VerificationResult(
            criterion_id="tests",
            status=VerificationStatus.PASS,
            message="Passed",
        ),
    ]
    
    feedback = build_retry_feedback(
        attempt_number=1,
        verification_results=results,
        missing_artifacts=[],
    )
    
    # No failures
    assert feedback.failures == []
    assert feedback.reviewer_findings is None
    assert feedback.missing_artifacts == []
