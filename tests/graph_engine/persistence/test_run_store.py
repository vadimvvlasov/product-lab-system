"""Test run state persistence."""

from graph_engine.models.enums import RunStatus, TaskStatus
from graph_engine.parser import parse_workflow
from graph_engine.persistence import create_run, load_run_state, save_run_state


def test_create_run(temp_dir):
    """Create a new run."""
    workflow_yaml = b"""
version: "1"
workflow:
  id: test
  description: Test
execution:
  max_concurrency: 2
  max_retries: 1
executors:
  mock:
    adapter: mock
    config: {}
executor_mapping: {}
tasks:
  - id: task-a
    type: test
    executor: mock
    verification:
      - id: check
        method: command
        command: "true"
"""
    
    workflow = parse_workflow(workflow_yaml)
    run_state, layout = create_run(workflow, workflow_yaml, temp_dir)
    
    assert run_state.run_id.startswith("test-")
    assert run_state.workflow_id == "test"
    assert run_state.status == RunStatus.RUNNING
    assert layout.run_root.exists()
    assert layout.workflow_snapshot.exists()
    assert layout.run_state.exists()
    
    # Task initialized as pending
    assert "task-a" in run_state.tasks
    assert run_state.tasks["task-a"].status == TaskStatus.PENDING


def test_save_and_load_run_state(temp_dir):
    """Save and load run state."""
    workflow_yaml = b"""
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
    verification:
      - id: check
        method: command
        command: "true"
"""
    
    workflow = parse_workflow(workflow_yaml)
    run_state, layout = create_run(workflow, workflow_yaml, temp_dir)
    
    # Modify state
    run_state.tasks["task-1"].status = TaskStatus.COMPLETED
    save_run_state(run_state, layout)
    
    # Load and verify
    loaded = load_run_state(layout)
    assert loaded.run_id == run_state.run_id
    assert loaded.tasks["task-1"].status == TaskStatus.COMPLETED
