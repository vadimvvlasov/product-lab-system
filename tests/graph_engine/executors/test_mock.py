"""Test mock executor."""

from pathlib import Path

from graph_engine.execution import ExecutionContext
from graph_engine.executors import MockExecutor, MockExecutorConfig
from graph_engine.models.enums import ExecutionStatus


def test_mock_executor_success(temp_dir):
    """Mock executor returns success."""
    config = MockExecutorConfig(
        result_status=ExecutionStatus.SUCCESS,
        result_summary="Task completed",
        result_artifacts=["output"],
    )
    
    executor = MockExecutor("test-executor", config)
    
    context = ExecutionContext(
        task_id="task-1",
        task_type="test",
        goal="Complete the task",
        acceptance_criteria=["Output exists"],
        input_artifacts={},
        required_outputs={"output": "artifacts/output.txt"},
        staging_dir=temp_dir,
    )
    
    result = executor.execute(context)
    
    assert result.status == ExecutionStatus.SUCCESS
    assert result.summary == "Task completed"
    assert "output" in result.artifacts
    assert executor.call_count == 1
    
    # Check artifact created
    assert (temp_dir / "artifacts" / "output.txt").exists()


def test_mock_executor_failure():
    """Mock executor returns failure."""
    config = MockExecutorConfig(
        result_status=ExecutionStatus.FAILURE,
        result_summary="Task failed",
        result_error="Something went wrong",
    )
    
    executor = MockExecutor("test", config)
    
    context = ExecutionContext(
        task_id="task-1",
        task_type="test",
        goal="Test",
        acceptance_criteria=[],
        input_artifacts={},
        required_outputs={},
        staging_dir=Path("/tmp"),
    )
    
    result = executor.execute(context)
    
    assert result.status == ExecutionStatus.FAILURE
    assert result.error == "Something went wrong"


def test_mock_executor_usage_reporting():
    """Mock executor reports usage."""
    config = MockExecutorConfig(
        report_usage=True,
        input_tokens=200,
        output_tokens=100,
    )
    
    executor = MockExecutor("test", config)
    
    context = ExecutionContext(
        task_id="task-1",
        task_type="test",
        goal="Test",
        acceptance_criteria=[],
        input_artifacts={},
        required_outputs={},
        staging_dir=Path("/tmp"),
    )
    
    result = executor.execute(context)
    
    assert result.usage is not None
    assert result.usage.input_tokens == 200
    assert result.usage.output_tokens == 100
    assert result.usage.available is True


def test_mock_executor_cancellation(temp_dir):
    """Mock executor respects cancellation."""
    config = MockExecutorConfig()
    executor = MockExecutor("test", config)
    
    # Cancel before execution
    executor.cancel()
    
    context = ExecutionContext(
        task_id="task-1",
        task_type="test",
        goal="Test",
        acceptance_criteria=[],
        input_artifacts={},
        required_outputs={},
        staging_dir=temp_dir,
    )
    
    result = executor.execute(context)
    
    assert result.status == ExecutionStatus.CANCELLED


def test_mock_executor_call_tracking():
    """Mock executor tracks calls."""
    config = MockExecutorConfig()
    executor = MockExecutor("test", config)
    
    context1 = ExecutionContext(
        task_id="task-1",
        task_type="test",
        goal="Test 1",
        acceptance_criteria=[],
        input_artifacts={},
        required_outputs={},
        staging_dir=Path("/tmp"),
    )
    
    context2 = ExecutionContext(
        task_id="task-2",
        task_type="test",
        goal="Test 2",
        acceptance_criteria=[],
        input_artifacts={},
        required_outputs={},
        staging_dir=Path("/tmp"),
    )
    
    executor.execute(context1)
    executor.execute(context2)
    
    assert executor.call_count == 2
    assert len(executor.calls) == 2
    assert executor.calls[0].task_id == "task-1"
    assert executor.calls[1].task_id == "task-2"
    
    executor.reset()
    assert executor.call_count == 0
    assert len(executor.calls) == 0
