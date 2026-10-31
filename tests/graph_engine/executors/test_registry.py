"""Test executor registry."""

import pytest

from graph_engine.errors import ExecutorError
from graph_engine.executors import ExecutorRegistry
from graph_engine.parser import parse_workflow


def test_registry_get_executor():
    """Registry creates and caches executors."""
    workflow_yaml = b"""
version: "1"
workflow:
  id: test
  description: Test
execution:
  max_concurrency: 1
  max_retries: 0
executors:
  mock-executor:
    adapter: mock
    config:
      summary: Custom summary
executor_mapping: {}
tasks:
  - id: task-1
    type: test
    executor: mock-executor
    verification:
      - id: check
        method: command
        command: "true"
"""
    
    workflow = parse_workflow(workflow_yaml)
    registry = ExecutorRegistry(workflow)
    
    executor = registry.get_executor("mock-executor")
    assert executor.name == "mock-executor"
    assert executor.adapter == "mock"
    
    # Second call returns same instance
    executor2 = registry.get_executor("mock-executor")
    assert executor is executor2


def test_registry_unknown_executor():
    """Registry raises error for undefined executor."""
    workflow_yaml = b"""
version: "1"
workflow:
  id: test
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
    
    workflow = parse_workflow(workflow_yaml)
    registry = ExecutorRegistry(workflow)
    
    with pytest.raises(ExecutorError, match="not defined"):
        registry.get_executor("undefined")


def test_registry_unknown_adapter():
    """Registry raises error for unknown adapter."""
    workflow_yaml = b"""
version: "1"
workflow:
  id: test
  description: Test
execution:
  max_concurrency: 1
  max_retries: 0
executors:
  unknown:
    adapter: future-adapter
    config: {}
executor_mapping: {}
tasks:
  - id: task-1
    type: test
    executor: unknown
    verification:
      - id: check
        method: command
        command: "true"
"""
    
    workflow = parse_workflow(workflow_yaml)
    registry = ExecutorRegistry(workflow)
    
    with pytest.raises(ExecutorError, match="Unknown adapter"):
        registry.get_executor("unknown")
