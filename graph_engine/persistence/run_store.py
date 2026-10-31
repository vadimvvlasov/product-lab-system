"""Run state persistence."""

from datetime import datetime, timezone
from pathlib import Path

from graph_engine import __version__
from graph_engine.models.enums import RunStatus, TaskStatus
from graph_engine.models.run import RunState, TaskState
from graph_engine.models.workflow import WorkflowDefinition
from graph_engine.persistence.atomic import atomic_read_json, atomic_write_json
from graph_engine.persistence.layout import RunLayout, generate_run_id
from graph_engine.persistence.snapshot import snapshot_executor_config, snapshot_workflow


def create_run(
    workflow: WorkflowDefinition,
    workflow_bytes: bytes,
    runs_dir: Path,
    run_id: str | None = None,
) -> tuple[RunState, RunLayout]:
    """
    Create a new run.
    
    Args:
        workflow: Parsed workflow definition
        workflow_bytes: Original YAML bytes
        runs_dir: Runs directory
        run_id: Optional explicit run ID
        
    Returns:
        (RunState, RunLayout) tuple
    """
    if run_id is None:
        run_id = generate_run_id(workflow.workflow.id)
    
    layout = RunLayout(runs_dir, run_id)
    layout.create_structure()
    
    # Snapshot workflow and config
    workflow_hash = snapshot_workflow(workflow_bytes, layout.workflow_snapshot)
    config_hash = snapshot_executor_config(workflow, layout.executor_config_snapshot)
    
    # Initialize task states
    tasks = {}
    for task in workflow.tasks:
        tasks[task.id] = TaskState(
            task_id=task.id,
            status=TaskStatus.PENDING,
        )
    
    # Create run state
    now = datetime.now(timezone.utc).isoformat()
    run_state = RunState(
        schema_version="1",
        run_id=run_id,
        workflow_id=workflow.workflow.id,
        status=RunStatus.RUNNING,
        created_at=now,
        workflow_snapshot_hash=workflow_hash,
        executor_config_hash=config_hash,
        engine_version=__version__,
        max_concurrency=workflow.execution.max_concurrency,
        max_retries=workflow.execution.max_retries,
        max_run_duration_minutes=workflow.execution.max_run_duration_minutes,
        tasks=tasks,
    )
    
    # Persist initial state
    save_run_state(run_state, layout)
    
    return run_state, layout


def save_run_state(run_state: RunState, layout: RunLayout):
    """Save run state atomically."""
    atomic_write_json(layout.run_state, run_state.to_dict())


def load_run_state(layout: RunLayout) -> RunState:
    """Load run state from disk."""
    data = atomic_read_json(layout.run_state)
    return RunState.from_dict(data)
