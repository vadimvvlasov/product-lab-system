"""Test reference validation."""

from graph_engine.models.enums import VerificationMethod
from graph_engine.models.workflow import (
    ExecutionLimits,
    ExecutorConfig,
    TaskDefinition,
    TaskInput,
    TaskOutput,
    VerificationCriterion,
    WorkflowDefinition,
    WorkflowMetadata,
)
from graph_engine.validation.references import validate_references


def test_duplicate_task_ids():
    """Duplicate task IDs must be rejected."""
    workflow = WorkflowDefinition(
        version="1",
        workflow=WorkflowMetadata(id="test", description="Test"),
        execution=ExecutionLimits(max_concurrency=1, max_retries=0),
        executors={"mock": ExecutorConfig(adapter="mock")},
        executor_mapping={},
        tasks=[
            TaskDefinition(
                id="task-1",
                type="test",
                executor="mock",
                verification=[VerificationCriterion(id="c", method=VerificationMethod.COMMAND, command="true")],
            ),
            TaskDefinition(
                id="task-1",
                type="test",
                executor="mock",
                verification=[VerificationCriterion(id="c", method=VerificationMethod.COMMAND, command="true")],
            ),
        ],
    )
    
    errors = validate_references(workflow)
    assert any("Duplicate task ID: 'task-1'" in err for err in errors)


def test_self_dependency():
    """Self-dependency must be rejected."""
    workflow = WorkflowDefinition(
        version="1",
        workflow=WorkflowMetadata(id="test", description="Test"),
        execution=ExecutionLimits(max_concurrency=1, max_retries=0),
        executors={"mock": ExecutorConfig(adapter="mock")},
        executor_mapping={},
        tasks=[
            TaskDefinition(
                id="task-1",
                type="test",
                executor="mock",
                depends_on=["task-1"],
                verification=[VerificationCriterion(id="c", method=VerificationMethod.COMMAND, command="true")],
            ),
        ],
    )
    
    errors = validate_references(workflow)
    assert any("self-dependency" in err for err in errors)


def test_nonexistent_dependency():
    """Non-existent dependency must be rejected."""
    workflow = WorkflowDefinition(
        version="1",
        workflow=WorkflowMetadata(id="test", description="Test"),
        execution=ExecutionLimits(max_concurrency=1, max_retries=0),
        executors={"mock": ExecutorConfig(adapter="mock")},
        executor_mapping={},
        tasks=[
            TaskDefinition(
                id="task-1",
                type="test",
                executor="mock",
                depends_on=["nonexistent"],
                verification=[VerificationCriterion(id="c", method=VerificationMethod.COMMAND, command="true")],
            ),
        ],
    )
    
    errors = validate_references(workflow)
    assert any("unknown task 'nonexistent'" in err for err in errors)


def test_input_from_non_dependency():
    """Input from non-dependency must be rejected."""
    workflow = WorkflowDefinition(
        version="1",
        workflow=WorkflowMetadata(id="test", description="Test"),
        execution=ExecutionLimits(max_concurrency=1, max_retries=0),
        executors={"mock": ExecutorConfig(adapter="mock")},
        executor_mapping={},
        tasks=[
            TaskDefinition(
                id="task-a",
                type="test",
                executor="mock",
                outputs=[TaskOutput(name="out", path="artifacts/a.txt")],
                verification=[VerificationCriterion(id="c", method=VerificationMethod.COMMAND, command="true")],
            ),
            TaskDefinition(
                id="task-b",
                type="test",
                executor="mock",
                inputs=[TaskInput(name="inp", from_task="task-a", artifact="out")],
                verification=[VerificationCriterion(id="c", method=VerificationMethod.COMMAND, command="true")],
            ),
        ],
    )
    
    errors = validate_references(workflow)
    assert any("is not in depends_on" in err for err in errors)


def test_input_from_undeclared_artifact():
    """Input from undeclared artifact must be rejected."""
    workflow = WorkflowDefinition(
        version="1",
        workflow=WorkflowMetadata(id="test", description="Test"),
        execution=ExecutionLimits(max_concurrency=1, max_retries=0),
        executors={"mock": ExecutorConfig(adapter="mock")},
        executor_mapping={},
        tasks=[
            TaskDefinition(
                id="task-a",
                type="test",
                executor="mock",
                outputs=[TaskOutput(name="out", path="artifacts/a.txt")],
                verification=[VerificationCriterion(id="c", method=VerificationMethod.COMMAND, command="true")],
            ),
            TaskDefinition(
                id="task-b",
                type="test",
                executor="mock",
                depends_on=["task-a"],
                inputs=[TaskInput(name="inp", from_task="task-a", artifact="missing")],
                verification=[VerificationCriterion(id="c", method=VerificationMethod.COMMAND, command="true")],
            ),
        ],
    )
    
    errors = validate_references(workflow)
    assert any("does not declare output artifact 'missing'" in err for err in errors)


def test_undefined_executor():
    """Undefined executor must be rejected."""
    workflow = WorkflowDefinition(
        version="1",
        workflow=WorkflowMetadata(id="test", description="Test"),
        execution=ExecutionLimits(max_concurrency=1, max_retries=0),
        executors={},
        executor_mapping={},
        tasks=[
            TaskDefinition(
                id="task-1",
                type="test",
                executor="undefined",
                verification=[VerificationCriterion(id="c", method=VerificationMethod.COMMAND, command="true")],
            ),
        ],
    )
    
    errors = validate_references(workflow)
    assert any("executor 'undefined' not defined" in err for err in errors)


def test_no_executor_resolution():
    """Task with no explicit executor and no mapping must be rejected."""
    workflow = WorkflowDefinition(
        version="1",
        workflow=WorkflowMetadata(id="test", description="Test"),
        execution=ExecutionLimits(max_concurrency=1, max_retries=0),
        executors={"mock": ExecutorConfig(adapter="mock")},
        executor_mapping={},
        tasks=[
            TaskDefinition(
                id="task-1",
                type="unmapped",
                verification=[VerificationCriterion(id="c", method=VerificationMethod.COMMAND, command="true")],
            ),
        ],
    )
    
    errors = validate_references(workflow)
    assert any("no explicit executor and no mapping" in err for err in errors)
