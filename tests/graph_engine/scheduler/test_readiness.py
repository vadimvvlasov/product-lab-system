"""Test task readiness computation."""

from graph_engine.models.enums import TaskStatus
from graph_engine.models.run import RunState, TaskState
from graph_engine.parser import parse_workflow
from graph_engine.scheduler import compute_ready_tasks


def test_compute_ready_independent_task():
    """Independent pending task is ready."""
    workflow_yaml = b"""
version: "1"
workflow:
  id: test
  description: Test
execution:
  max_concurrency: 2
  max_retries: 0
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
    run_state = RunState(
        schema_version="1",
        run_id="test-run",
        workflow_id="test",
        status="running",
        created_at="2026-10-31T00:00:00Z",
        tasks={"task-a": TaskState(task_id="task-a", status=TaskStatus.PENDING)},
    )
    
    ready, blocked = compute_ready_tasks(workflow, run_state, 2)
    
    assert "task-a" in ready
    assert len(blocked) == 0


def test_compute_ready_waits_for_dependency():
    """Task waits for dependency to complete."""
    workflow_yaml = b"""
version: "1"
workflow:
  id: test
  description: Test
execution:
  max_concurrency: 2
  max_retries: 0
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
  - id: task-b
    type: test
    executor: mock
    depends_on: [task-a]
    verification:
      - id: check
        method: command
        command: "true"
"""
    
    workflow = parse_workflow(workflow_yaml)
    run_state = RunState(
        schema_version="1",
        run_id="test-run",
        workflow_id="test",
        status="running",
        created_at="2026-10-31T00:00:00Z",
        tasks={
            "task-a": TaskState(task_id="task-a", status=TaskStatus.RUNNING),
            "task-b": TaskState(task_id="task-b", status=TaskStatus.PENDING),
        },
    )
    
    ready, blocked = compute_ready_tasks(workflow, run_state, 2)
    
    assert "task-b" not in ready  # Still waiting
    assert "task-b" not in blocked


def test_compute_ready_concurrency_limit():
    """Respects max_concurrency limit."""
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
  - id: task-a
    type: test
    executor: mock
    verification:
      - id: check
        method: command
        command: "true"
  - id: task-b
    type: test
    executor: mock
    verification:
      - id: check
        method: command
        command: "true"
"""
    
    workflow = parse_workflow(workflow_yaml)
    run_state = RunState(
        schema_version="1",
        run_id="test-run",
        workflow_id="test",
        status="running",
        created_at="2026-10-31T00:00:00Z",
        tasks={
            "task-a": TaskState(task_id="task-a", status=TaskStatus.RUNNING),
            "task-b": TaskState(task_id="task-b", status=TaskStatus.PENDING),
        },
    )
    
    ready, blocked = compute_ready_tasks(workflow, run_state, 1)
    
    # task-b is not ready because concurrency limit reached
    assert "task-b" not in ready


def test_dependency_failure_blocks_downstream():
    """Failed dependency blocks downstream task."""
    workflow_yaml = b"""
version: "1"
workflow:
  id: test
  description: Test
execution:
  max_concurrency: 2
  max_retries: 0
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
  - id: task-b
    type: test
    executor: mock
    depends_on: [task-a]
    verification:
      - id: check
        method: command
        command: "true"
"""
    
    workflow = parse_workflow(workflow_yaml)
    run_state = RunState(
        schema_version="1",
        run_id="test-run",
        workflow_id="test",
        status="running",
        created_at="2026-10-31T00:00:00Z",
        tasks={
            "task-a": TaskState(task_id="task-a", status=TaskStatus.BLOCKED),
            "task-b": TaskState(task_id="task-b", status=TaskStatus.PENDING),
        },
    )
    
    ready, blocked = compute_ready_tasks(workflow, run_state, 2)
    
    assert "task-b" not in ready
    assert "task-b" in blocked
