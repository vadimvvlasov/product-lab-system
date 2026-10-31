"""Task readiness computation (pure functions)."""

from graph_engine.models.enums import TaskStatus
from graph_engine.models.run import RunState
from graph_engine.models.workflow import WorkflowDefinition


def compute_ready_tasks(
    workflow: WorkflowDefinition,
    run_state: RunState,
    max_concurrency: int,
) -> tuple[list[str], list[str]]:
    """
    Compute which tasks are ready to run and which should be blocked.
    
    Pure function: no side effects, deterministic given inputs.
    
    Args:
        workflow: Workflow definition
        run_state: Current run state
        max_concurrency: Maximum concurrent tasks
        
    Returns:
        (ready_task_ids, newly_blocked_task_ids)
    """
    ready = []
    newly_blocked = []
    
    # Count running tasks
    running_count = sum(
        1 for task in run_state.tasks.values()
        if task.status == TaskStatus.RUNNING
    )
    
    for task_def in workflow.tasks:
        task_state = run_state.tasks.get(task_def.id)
        if not task_state:
            continue
        
        # Only process pending/retrying tasks
        if task_state.status not in (TaskStatus.PENDING, TaskStatus.RETRYING):
            continue
        
        # Check if should be blocked
        block_reason = _should_block(task_def, run_state, workflow)
        if block_reason:
            newly_blocked.append(task_def.id)
            continue
        
        # Check readiness
        if _is_ready(task_def, run_state, running_count, max_concurrency):
            ready.append(task_def.id)
    
    return ready, newly_blocked


def _is_ready(
    task_def,
    run_state: RunState,
    running_count: int,
    max_concurrency: int,
) -> bool:
    """Check if task is ready to dispatch."""
    task_state = run_state.tasks.get(task_def.id)
    if not task_state:
        return False
    
    # Must be pending or retrying
    if task_state.status not in (TaskStatus.PENDING, TaskStatus.RETRYING):
        return False
    
    # Check concurrency slots
    if running_count >= max_concurrency:
        return False
    
    # Check dependencies completed
    for dep_id in task_def.depends_on:
        dep_state = run_state.tasks.get(dep_id)
        if not dep_state or dep_state.status != TaskStatus.COMPLETED:
            return False
    
    # Check approval for before_execution
    if task_def.approval.value == "required" and task_def.approval_point.value == "before_execution":
        # Would need approval check here (Stage 5)
        pass
    
    return True


def _should_block(task_def, run_state: RunState, workflow: WorkflowDefinition) -> str | None:
    """Check if task should be blocked. Returns block reason or None."""
    task_state = run_state.tasks.get(task_def.id)
    if not task_state:
        return None
    
    # Check dependency failures
    for dep_id in task_def.depends_on:
        dep_state = run_state.tasks.get(dep_id)
        if dep_state and dep_state.status in (TaskStatus.BLOCKED, TaskStatus.FAILED):
            return f"dependency '{dep_id}' {dep_state.status.value}"
    
    return None
