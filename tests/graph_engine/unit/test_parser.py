"""Test YAML parsing."""

import pytest

from graph_engine.errors import WorkflowParseError
from graph_engine.parser import parse_workflow


def test_parse_valid_workflow():
    """Parse a minimal valid workflow."""
    yaml_content = b"""
version: "1"
workflow:
  id: test-wf
  description: Test workflow
execution:
  max_concurrency: 1
  max_retries: 0
executors:
  mock:
    adapter: mock
    config: {}
executor_mapping: {}
tasks:
  - id: task-1
    type: test
    executor: mock
    verification:
      - id: always-pass
        method: command
        command: "true"
"""
    
    workflow = parse_workflow(yaml_content)
    assert workflow.version == "1"
    assert workflow.workflow.id == "test-wf"
    assert workflow.execution.max_concurrency == 1
    assert len(workflow.tasks) == 1
    assert workflow.tasks[0].id == "task-1"


def test_reject_duplicate_keys():
    """Duplicate YAML keys must be rejected."""
    yaml_content = b"""
version: "1"
workflow:
  id: test
  id: duplicate
  description: Test
execution:
  max_concurrency: 1
  max_retries: 0
executors: {}
executor_mapping: {}
tasks:
  - id: task-1
    type: test
    executor: mock
    verification:
      - id: check
        method: command
        command: "true"
"""
    
    with pytest.raises(WorkflowParseError, match="Duplicate key 'id'"):
        parse_workflow(yaml_content)


def test_reject_multiple_documents():
    """Multiple YAML documents must be rejected."""
    yaml_content = b"""
version: "1"
workflow:
  id: test
  description: Test
---
version: "1"
workflow:
  id: test2
  description: Test2
"""
    
    with pytest.raises(WorkflowParseError, match="Multiple YAML documents"):
        parse_workflow(yaml_content)


def test_reject_empty_document():
    """Empty YAML must be rejected."""
    with pytest.raises(WorkflowParseError, match="Empty YAML"):
        parse_workflow(b"")


def test_reject_wrong_version():
    """Unsupported version must be rejected."""
    yaml_content = b"""
version: "2"
workflow:
  id: test
  description: Test
execution:
  max_concurrency: 1
  max_retries: 0
executors: {}
executor_mapping: {}
tasks: []
"""
    
    with pytest.raises(WorkflowParseError, match="Unsupported workflow version"):
        parse_workflow(yaml_content)


def test_reject_empty_tasks():
    """Tasks list must not be empty."""
    yaml_content = b"""
version: "1"
workflow:
  id: test
  description: Test
execution:
  max_concurrency: 1
  max_retries: 0
executors: {}
executor_mapping: {}
tasks: []
"""
    
    with pytest.raises(WorkflowParseError, match="non-empty list"):
        parse_workflow(yaml_content)


def test_reject_missing_verification():
    """Verification must be non-empty."""
    yaml_content = b"""
version: "1"
workflow:
  id: test
  description: Test
execution:
  max_concurrency: 1
  max_retries: 0
executors:
  mock:
    adapter: mock
    config: {}
executor_mapping: {}
tasks:
  - id: task-1
    type: test
    executor: mock
    verification: []
"""
    
    with pytest.raises(WorkflowParseError, match="non-empty list"):
        parse_workflow(yaml_content)
