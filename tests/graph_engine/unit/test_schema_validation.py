"""Test schema validation."""

import pytest

from graph_engine.models.enums import ApprovalRequirement, SideEffects, VerificationMethod
from graph_engine.models.workflow import (
    ExecutionLimits,
    ExecutorConfig,
    TaskDefinition,
    TaskOutput,
    VerificationCriterion,
    WorkflowDefinition,
    WorkflowMetadata,
)
from graph_engine.validation.schema import validate_schema


def test_invalid_task_id():
    """Task ID must be filesystem-safe."""
    workflow = WorkflowDefinition(
        version="1",
        workflow=WorkflowMetadata(id="test", description="Test"),
        execution=ExecutionLimits(max_concurrency=1, max_retries=0),
        executors={"mock": ExecutorConfig(adapter="mock")},
        executor_mapping={},
        tasks=[
            TaskDefinition(
                id="task with spaces",
                type="test",
                executor="mock",
                verification=[
                    VerificationCriterion(id="check", method=VerificationMethod.COMMAND, command="true")
                ],
            )
        ],
    )
    
    errors = validate_schema(workflow)
    assert len(errors) > 0
    assert any("filesystem-safe" in err for err in errors)


def test_output_path_must_be_relative():
    """Output paths must be relative."""
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
                verification=[
                    VerificationCriterion(id="check", method=VerificationMethod.COMMAND, command="true")
                ],
                outputs=[TaskOutput(name="out", path="/absolute/path.txt")],
            )
        ],
    )
    
    errors = validate_schema(workflow)
    assert any("must be relative" in err for err in errors)


def test_output_path_must_start_with_artifacts():
    """Output paths must start with artifacts/."""
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
                verification=[
                    VerificationCriterion(id="check", method=VerificationMethod.COMMAND, command="true")
                ],
                outputs=[TaskOutput(name="out", path="output.txt")],
            )
        ],
    )
    
    errors = validate_schema(workflow)
    assert any("must start with 'artifacts/'" in err for err in errors)


def test_verification_command_requires_command_field():
    """Command verification must have command field."""
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
                verification=[
                    VerificationCriterion(id="check", method=VerificationMethod.COMMAND, command=None)
                ],
            )
        ],
    )
    
    errors = validate_schema(workflow)
    assert any("requires 'command' field" in err for err in errors)


def test_side_effects_requires_idempotency_key():
    """Idempotent/unsafe tasks must have idempotency_key."""
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
                side_effects=SideEffects.UNSAFE,
                idempotency_key=None,
                verification=[
                    VerificationCriterion(id="check", method=VerificationMethod.COMMAND, command="true")
                ],
            )
        ],
    )
    
    errors = validate_schema(workflow)
    assert any("requires 'idempotency_key'" in err for err in errors)
