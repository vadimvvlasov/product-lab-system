"""Test DAG validation and cycle detection."""

import pytest

from graph_engine.errors import DAGCycleError
from graph_engine.models.enums import VerificationMethod
from graph_engine.models.workflow import (
    ExecutionLimits,
    ExecutorConfig,
    TaskDefinition,
    VerificationCriterion,
    WorkflowDefinition,
    WorkflowMetadata,
)
from graph_engine.validation.dag import validate_dag


def test_valid_dag():
    """Valid DAG produces topological order."""
    workflow = WorkflowDefinition(
        version="1",
        workflow=WorkflowMetadata(id="test", description="Test"),
        execution=ExecutionLimits(max_concurrency=1, max_retries=0),
        executors={"mock": ExecutorConfig(adapter="mock")},
        executor_mapping={},
        tasks=[
            TaskDefinition(
                id="a",
                type="test",
                executor="mock",
                verification=[VerificationCriterion(id="c", method=VerificationMethod.COMMAND, command="true")],
            ),
            TaskDefinition(
                id="b",
                type="test",
                executor="mock",
                depends_on=["a"],
                verification=[VerificationCriterion(id="c", method=VerificationMethod.COMMAND, command="true")],
            ),
            TaskDefinition(
                id="c",
                type="test",
                executor="mock",
                depends_on=["a"],
                verification=[VerificationCriterion(id="c", method=VerificationMethod.COMMAND, command="true")],
            ),
        ],
    )
    
    order, cycle = validate_dag(workflow)
    assert len(order) == 3
    assert order[0] == "a"
    assert set(order[1:]) == {"b", "c"}
    assert cycle == []


def test_two_node_cycle():
    """Two-node cycle must be detected."""
    workflow = WorkflowDefinition(
        version="1",
        workflow=WorkflowMetadata(id="test", description="Test"),
        execution=ExecutionLimits(max_concurrency=1, max_retries=0),
        executors={"mock": ExecutorConfig(adapter="mock")},
        executor_mapping={},
        tasks=[
            TaskDefinition(
                id="a",
                type="test",
                executor="mock",
                depends_on=["b"],
                verification=[VerificationCriterion(id="c", method=VerificationMethod.COMMAND, command="true")],
            ),
            TaskDefinition(
                id="b",
                type="test",
                executor="mock",
                depends_on=["a"],
                verification=[VerificationCriterion(id="c", method=VerificationMethod.COMMAND, command="true")],
            ),
        ],
    )
    
    with pytest.raises(DAGCycleError) as exc_info:
        validate_dag(workflow)
    
    assert "cycle" in str(exc_info.value).lower()
    assert len(exc_info.value.cycle_path) > 0


def test_larger_cycle():
    """Larger cycle must be detected."""
    workflow = WorkflowDefinition(
        version="1",
        workflow=WorkflowMetadata(id="test", description="Test"),
        execution=ExecutionLimits(max_concurrency=1, max_retries=0),
        executors={"mock": ExecutorConfig(adapter="mock")},
        executor_mapping={},
        tasks=[
            TaskDefinition(
                id="a",
                type="test",
                executor="mock",
                verification=[VerificationCriterion(id="c", method=VerificationMethod.COMMAND, command="true")],
            ),
            TaskDefinition(
                id="b",
                type="test",
                executor="mock",
                depends_on=["a"],
                verification=[VerificationCriterion(id="c", method=VerificationMethod.COMMAND, command="true")],
            ),
            TaskDefinition(
                id="c",
                type="test",
                executor="mock",
                depends_on=["b"],
                verification=[VerificationCriterion(id="c", method=VerificationMethod.COMMAND, command="true")],
            ),
            TaskDefinition(
                id="d",
                type="test",
                executor="mock",
                depends_on=["c", "a"],  # Creates cycle: a -> b -> c -> a
                verification=[VerificationCriterion(id="c", method=VerificationMethod.COMMAND, command="true")],
            ),
        ],
    )
    
    # Manually create a cycle by having 'a' depend on 'd'
    workflow.tasks[0].depends_on.append("d")
    
    with pytest.raises(DAGCycleError):
        validate_dag(workflow)
