"""Tests for agent verification."""

import pytest

from graph_engine.executors.mock import MockExecutor, MockExecutorConfig
from graph_engine.models.enums import ExecutionStatus
from graph_engine.verification.agent import AgentVerifier
from graph_engine.verification.base import (
    VerificationCriterion,
    VerificationMethod,
    VerificationStatus,
)


@pytest.fixture
def temp_staging(tmp_path):
    """Create temporary staging directory."""
    staging = tmp_path / "staging"
    staging.mkdir()
    return staging


class SimpleRegistry:
    """Simple registry for testing."""

    def __init__(self):
        self._executors = {}

    def get(self, name: str):
        if name not in self._executors:
            raise KeyError(f"Executor {name} not found")
        return self._executors[name]

    def register(self, name: str, executor):
        self._executors[name] = executor


@pytest.fixture
def mock_registry():
    """Create simple mock executor registry for testing."""
    registry = SimpleRegistry()

    # Add passing reviewer
    passing_config = MockExecutorConfig(
        result_status=ExecutionStatus.SUCCESS,
        result_summary="Review passed",
    )
    passing_reviewer = MockExecutor("passing_reviewer", passing_config)
    registry.register("passing_reviewer", passing_reviewer)

    # Add failing reviewer with findings
    failing_config = MockExecutorConfig(
        result_status=ExecutionStatus.FAILURE,
        result_summary="Review failed",
        result_error="Issues found",
    )
    failing_reviewer = MockExecutor("failing_reviewer", failing_config)
    registry.register("failing_reviewer", failing_reviewer)

    return registry


def test_agent_verification_pass(mock_registry, temp_staging):
    """Test passing agent verification."""
    verifier = AgentVerifier(mock_registry)

    criterion = VerificationCriterion(
        id="reviewer",
        method=VerificationMethod.AGENT,
        executor="passing_reviewer",
        acceptance_criteria="Check code quality",
    )

    task_context = {
        "task_id": "task1",
        "input_artifacts": {},
        "required_outputs": {},
    }

    result = verifier.verify(criterion, temp_staging, task_context)

    assert result.status == VerificationStatus.PASS
    assert result.criterion_id == "reviewer"
    assert "passed" in result.message.lower()


def test_agent_verification_fail(mock_registry, temp_staging):
    """Test failing agent verification with findings."""
    verifier = AgentVerifier(mock_registry)

    # Create a custom failing executor that returns findings
    failing_config = MockExecutorConfig(
        result_status=ExecutionStatus.FAILURE,
        result_summary="Review failed",
        result_error="Found issues",
    )
    custom_executor = MockExecutor("custom_failing", failing_config)

    # Override execute to add findings in metadata
    original_execute = custom_executor.execute

    def execute_with_findings(context):
        result = original_execute(context)
        result.metadata["findings"] = ["Issue 1", "Issue 2"]
        return result

    custom_executor.execute = execute_with_findings

    mock_registry.register("custom_failing", custom_executor)

    criterion = VerificationCriterion(
        id="reviewer",
        method=VerificationMethod.AGENT,
        executor="custom_failing",
        acceptance_criteria="Check code quality",
    )

    task_context = {
        "task_id": "task1",
        "input_artifacts": {},
        "required_outputs": {},
    }

    result = verifier.verify(criterion, temp_staging, task_context)

    assert result.status == VerificationStatus.FAIL
    assert result.criterion_id == "reviewer"
    assert len(result.findings) == 2
    assert "Issue 1" in result.findings
    assert "Issue 2" in result.findings


def test_agent_verification_missing_executor_field(mock_registry, temp_staging):
    """Test error when executor field is missing."""
    verifier = AgentVerifier(mock_registry)

    criterion = VerificationCriterion(
        id="reviewer",
        method=VerificationMethod.AGENT,
        executor=None,  # Missing!
    )

    task_context = {"task_id": "task1"}

    result = verifier.verify(criterion, temp_staging, task_context)

    assert result.status == VerificationStatus.ERROR
    assert "missing 'executor'" in result.message.lower()


def test_agent_verification_unknown_executor(mock_registry, temp_staging):
    """Test error when executor not found."""
    verifier = AgentVerifier(mock_registry)

    criterion = VerificationCriterion(
        id="reviewer",
        method=VerificationMethod.AGENT,
        executor="unknown_executor",
    )

    task_context = {"task_id": "task1"}

    result = verifier.verify(criterion, temp_staging, task_context)

    assert result.status == VerificationStatus.ERROR
    assert "not found" in result.message.lower()


def test_agent_verification_fresh_context(mock_registry, temp_staging):
    """Test that reviewer receives fresh context."""
    verifier = AgentVerifier(mock_registry)

    criterion = VerificationCriterion(
        id="reviewer",
        method=VerificationMethod.AGENT,
        executor="passing_reviewer",
        acceptance_criteria="Verify task completion",
    )

    task_context = {
        "task_id": "implementation",
        "input_artifacts": {},
        "required_outputs": {"report": "report.md"},
    }

    result = verifier.verify(criterion, temp_staging, task_context)

    # Check that executor was called
    executor = mock_registry.get("passing_reviewer")
    assert executor.call_count == 1

    # Verify context was fresh (attempt_number=1, no retry_feedback)
    call_context = executor.last_context
    assert call_context.attempt_number == 1
    assert call_context.retry_feedback is None
    assert call_context.task_type == "verification"


def test_agent_verifier_does_not_see_implementer_transcript(
    mock_registry, temp_staging
):
    """Test that reviewer does NOT see implementer's conversation."""
    verifier = AgentVerifier(mock_registry)

    criterion = VerificationCriterion(
        id="reviewer",
        method=VerificationMethod.AGENT,
        executor="passing_reviewer",
        acceptance_criteria="Independent review",
    )

    # Task context does NOT include implementer transcript
    task_context = {
        "task_id": "task1",
        "input_artifacts": {},
        "required_outputs": {},
        # No "implementer_conversation" field
    }

    result = verifier.verify(criterion, temp_staging, task_context)

    # Verification uses fresh context
    executor = mock_registry.get("passing_reviewer")
    context = executor.last_context

    # Context should NOT have implementer transcript
    assert context.attempt_number == 1
    assert context.retry_feedback is None
    # Goal comes from acceptance_criteria, not implementer
    assert "independent review" in context.goal.lower()
