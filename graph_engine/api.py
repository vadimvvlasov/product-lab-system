"""Public API for graph engine integration."""

from pathlib import Path
from typing import Optional, Union

from graph_engine.errors import ValidationError
from graph_engine.execution.controller import RunController
from graph_engine.models.run import RunState
from graph_engine.models.workflow import WorkflowDefinition
from graph_engine.parser import parse_workflow, parse_workflow_file
from graph_engine.persistence.approval_store import ApprovalStore
from graph_engine.persistence.layout import RunLayout
from graph_engine.persistence.run_store import (
    create_run,
    load_run_state,
    save_run_state,
)
from graph_engine.recovery.recovery import RecoveryManager
from graph_engine.validation import ValidationReport, validate_workflow


def validate_workflow_file(workflow_path: Union[str, Path]) -> ValidationReport:
    """
    Load and validate a workflow file.

    This is the stable public API for workflow validation.
    """
    path = Path(workflow_path)
    workflow, _ = parse_workflow_file(path)
    return validate_workflow(workflow)


def run_workflow(
    workflow_path: Union[str, Path],
    runs_dir: Union[str, Path],
    run_id: Optional[str] = None,
) -> tuple[RunState, RunLayout]:
    """
    Validate a workflow, create a run, and execute it.

    Returns:
        (RunState, RunLayout) after the run pauses or finishes.
    """
    workflow, raw = parse_workflow_file(Path(workflow_path))
    report = validate_workflow(workflow)
    if not report.is_valid:
        raise ValidationError("; ".join(report.errors))

    state, layout = create_run(workflow, raw, Path(runs_dir), run_id=run_id)
    state = RunController(workflow, layout, state).run()
    return state, layout


def load_status(run_dir: Union[str, Path]) -> RunState:
    """Load persisted run state."""
    run_path = Path(run_dir)
    return load_run_state(RunLayout(run_path.parent, run_path.name))


def resume_run(
    run_dir: Union[str, Path],
    extend_run_timeout_minutes: int = 0,
) -> RunState:
    """
    Reconcile an interrupted or paused run and continue execution.

    Args:
        run_dir: Run directory
        extend_run_timeout_minutes: Extra minutes added to the run timeout
    """
    run_path = Path(run_dir)
    info = RecoveryManager(run_path).resume_workflow()
    state: RunState = info["updated_state"]
    workflow: WorkflowDefinition = info["workflow"]

    if extend_run_timeout_minutes:
        base = state.max_run_duration_minutes or 0
        state.max_run_duration_minutes = base + extend_run_timeout_minutes

    layout = RunLayout(run_path.parent, run_path.name)
    layout.cancel_sentinel.unlink(missing_ok=True)
    save_run_state(state, layout)
    return RunController(workflow, layout, state).run()


def approve_task(
    run_dir: Union[str, Path],
    task_id: str,
    approver: Optional[str] = None,
    comment: Optional[str] = None,
) -> None:
    """Record a human approval for a task."""
    ApprovalStore(Path(run_dir)).record_approval(
        task_id, True, approver=approver, comment=comment
    )


def reject_task(
    run_dir: Union[str, Path],
    task_id: str,
    approver: Optional[str] = None,
    comment: Optional[str] = None,
) -> None:
    """Record a human rejection for a task."""
    ApprovalStore(Path(run_dir)).record_approval(
        task_id, False, approver=approver, comment=comment
    )


def cancel_run(run_dir: Union[str, Path]) -> None:
    """Request cancellation of a running run."""
    run_path = Path(run_dir)
    RunLayout(run_path.parent, run_path.name).cancel_sentinel.write_text("cancel")


__all__ = [
    "approve_task",
    "cancel_run",
    "load_status",
    "parse_workflow",
    "reject_task",
    "resume_run",
    "run_workflow",
    "validate_workflow_file",
    "ValidationReport",
]
