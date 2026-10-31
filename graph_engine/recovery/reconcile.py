"""State reconciliation after interruption."""

from dataclasses import dataclass
from pathlib import Path

from graph_engine.models.enums import TaskStatus


@dataclass
class TaskReconciliation:
    """Reconciliation decision for a task."""

    task_id: str
    old_status: TaskStatus
    new_status: TaskStatus
    reason: str
    safe: bool  # False if human intervention required

    # Artifact validation
    artifacts_valid: bool = True
    missing_artifacts: list[str] = None

    # For completed tasks
    reuse: bool = False  # Can reuse completed work


def reconcile_task_status(
    task_id: str,
    current_status: TaskStatus,
    artifacts_dir: Path,
    required_artifacts: list[dict],
    side_effects: str = "none",
) -> TaskReconciliation:
    """
    Reconcile task status after interruption.

    Args:
        task_id: Task identifier
        current_status: Status from persisted state
        artifacts_dir: Run directory (artifacts paths are relative to this)
        required_artifacts: List of required artifact specs
        side_effects: Side effects policy (none/idempotent/unsafe)

    Returns:
        Reconciliation decision
    """
    # Terminal states stay terminal
    if current_status in (TaskStatus.BLOCKED, TaskStatus.FAILED):
        return TaskReconciliation(
            task_id=task_id,
            old_status=current_status,
            new_status=current_status,
            reason="Terminal state preserved",
            safe=True,
        )

    # Completed tasks: validate artifacts
    if current_status == TaskStatus.COMPLETED:
        missing = []
        for artifact_spec in required_artifacts:
            # artifact_spec["path"] is relative to run_dir, e.g. "artifacts/output.txt"
            artifact_path = artifacts_dir / artifact_spec["path"]
            if not artifact_path.exists():
                missing.append(artifact_spec["name"])

        if missing:
            # Artifacts missing - must re-execute
            if side_effects == "unsafe":
                # Cannot safely re-execute
                return TaskReconciliation(
                    task_id=task_id,
                    old_status=current_status,
                    new_status=TaskStatus.BLOCKED,
                    reason=f"Artifacts missing but side_effects=unsafe: {missing}",
                    safe=False,
                    artifacts_valid=False,
                    missing_artifacts=missing,
                )
            else:
                # Safe to re-execute
                return TaskReconciliation(
                    task_id=task_id,
                    old_status=current_status,
                    new_status=TaskStatus.PENDING,
                    reason=f"Artifacts missing, will re-execute: {missing}",
                    safe=True,
                    artifacts_valid=False,
                    missing_artifacts=missing,
                )

        # Artifacts exist - can reuse
        return TaskReconciliation(
            task_id=task_id,
            old_status=current_status,
            new_status=TaskStatus.COMPLETED,
            reason="Artifacts validated, reusing completed task",
            safe=True,
            artifacts_valid=True,
            reuse=True,
        )

    # Running/verifying: interrupted
    if current_status in (TaskStatus.RUNNING, TaskStatus.VERIFYING):
        if side_effects == "unsafe":
            # Cannot safely restart
            return TaskReconciliation(
                task_id=task_id,
                old_status=current_status,
                new_status=TaskStatus.BLOCKED,
                reason=f"Interrupted during {current_status.value}, side_effects=unsafe",
                safe=False,
            )
        else:
            # Safe to restart
            return TaskReconciliation(
                task_id=task_id,
                old_status=current_status,
                new_status=TaskStatus.PENDING,
                reason=f"Interrupted during {current_status.value}, will restart",
                safe=True,
            )

    # Ready/retrying: return to pending
    if current_status in (TaskStatus.READY, TaskStatus.RETRYING):
        return TaskReconciliation(
            task_id=task_id,
            old_status=current_status,
            new_status=TaskStatus.PENDING,
            reason=f"Reset {current_status.value} to pending",
            safe=True,
        )

    # Pending: keep pending
    if current_status == TaskStatus.PENDING:
        return TaskReconciliation(
            task_id=task_id,
            old_status=current_status,
            new_status=TaskStatus.PENDING,
            reason="Pending state preserved",
            safe=True,
        )

    # Unknown state
    return TaskReconciliation(
        task_id=task_id,
        old_status=current_status,
        new_status=TaskStatus.BLOCKED,
        reason=f"Unknown status: {current_status}",
        safe=False,
    )
