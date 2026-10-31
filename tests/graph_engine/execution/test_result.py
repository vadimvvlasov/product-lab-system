"""Test execution result validation."""

from graph_engine.execution import ExecutionResult, Usage, validate_result
from graph_engine.models.enums import ExecutionStatus


def test_validate_valid_result():
    """Valid result passes validation."""
    result = ExecutionResult(
        status=ExecutionStatus.SUCCESS,
        summary="Task completed successfully",
        artifacts=["output"],
        usage=Usage(input_tokens=100, output_tokens=50, available=True),
    )
    
    errors = validate_result(result)
    assert len(errors) == 0


def test_validate_missing_summary():
    """Validation catches missing summary."""
    result = ExecutionResult(
        status=ExecutionStatus.SUCCESS,
        summary="",
    )
    
    errors = validate_result(result)
    assert any("Summary is required" in err for err in errors)


def test_validate_negative_usage():
    """Validation catches negative usage values."""
    result = ExecutionResult(
        status=ExecutionStatus.SUCCESS,
        summary="Test",
        usage=Usage(input_tokens=-10, output_tokens=-5),
    )
    
    errors = validate_result(result)
    assert any("input_tokens" in err for err in errors)
    assert any("output_tokens" in err for err in errors)


def test_usage_unavailable():
    """Usage can be marked unavailable."""
    usage = Usage(available=False)
    
    assert usage.input_tokens is None
    assert usage.output_tokens is None
    assert usage.estimated_cost is None
    assert usage.available is False
