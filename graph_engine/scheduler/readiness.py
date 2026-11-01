"""Task readiness computation (pure functions)."""

from dataclasses import dataclass, field

from graph_engine.models.enums import ApprovalPoint, ApprovalRequirement, TaskStatus
from graph_engine.models.run import RunState
from graph_engine.models.workflow import TaskDefinition, WorkflowDefinition


@dataclass
class ReadinessPlan:
    """Result of a readiness computation."""

    ready: list[str] = field(default_factory=list)
    blocked: dict[str, str] = field(default_factory=dict)
    awaiting_approval: list[str] = field(default_factory=list)


def compute_ready_tasks(
    workflow: WorkflowDefinition,
    run_state: RunState,
    max_concurrency: int,
    approved_task_ids: frozenset[str] = frozenset(),
) -> ReadinessPlan:
    """
    Compute which tasks are ready, blocked, or waiting for approval.

    Pure function: no side effects, deterministic given inputs.

    Args:
        workflow: Workflow definition
        run_state: Current run state
        max_concurrency: Maximum concurrent tasks
        approved_task_ids: Tasks with a recorded human approval

    Returns:
        ReadinessPlan with ready, blocked (reason per task), awaiting_approval
    """
    plan = ReadinessPlan()

    # Propagate blocking transitively before dispatching anything.
    blocked_ids: set[str] = set()
    changed = True
    while changed:
        changed = False
        for task in workflow.tasks:
            if task.id in blocked_ids:
                continue
            reason = _block_reason(task, run_state, blocked_ids)
            if reason is not None:
                plan.blocked[task.id] = reason
                blocked_ids.add(task.id)
                changed = True

    running_count = sum(
        1 for task in run_state.tasks.values()
        if task.status == TaskStatus.RUNNING
    )
    available_slots = max(0, max_concurrency - running_count)

    for task in workflow.tasks:
        task_state = run_state.tasks.get(task.id)
        if not task_state:
            continue
        if task_state.status not in (TaskStatus.PENDING, TaskStatus.RETRYING):
            continue
        if task.id in blocked_ids:
            continue

        # Dependencies must be completed; otherwise the task simply waits.
        if not _dependencies_completed(task, run_state):
            continue

        if _needs_approval(task) and task.id not in approved_task_ids:
            plan.awaiting_approval.append(task.id)
            continue

        if available_slots <= 0:
            continue

        plan.ready.append(task.id)
        available_slots -= 1

    return plan


def _needs_approval(task: TaskDefinition) -> bool:
    return (
        task.approval == ApprovalRequirement.REQUIRED
        and task.approval_point == ApprovalPoint.BEFORE_EXECUTION
    )


def _dependencies_completed(task: TaskDefinition, run_state: RunState) -> bool:
    for dep_id in task.depends_on:
        dep_state = run_state.tasks.get(dep_id)
        if not dep_state or dep_state.status != TaskStatus.COMPLETED:
            return False
    return True


def _block_reason(
    task: TaskDefinition,
    run_state: RunState,
    blocked_ids: set[str],
) -> str | None:
    """Return a block reason if the task cannot run because of a dependency."""
    for dep_id in task.depends_on:
        if dep_id in blocked_ids:
            return f"dependency '{dep_id}' blocked"
        dep_state = run_state.tasks.get(dep_id)
        if dep_state and dep_state.status in (TaskStatus.BLOCKED, TaskStatus.FAILED):
            return f"dependency '{dep_id}' {dep_state.status.value}"
    return None
