"""State reconciliation after interruption."""

import hashlib
from dataclasses import dataclass, field
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
    missing_artifacts: list[str] = field(default_factory=list)

    # For completed tasks
    reuse: bool = False  # Can reuse completed work
    resume_phase: str | None = None  # "publish" when verification already ran


def reconcile_task_status(
    task_id: str,
    current_status: TaskStatus,
    artifacts_dir: Path,
    required_artifacts: list[dict],
    side_effects: str = "none",
    staging_dir: Path | None = None,
    require_checksum: bool = False,
) -> TaskReconciliation:
    """
    Reconcile task status after interruption.

    Args:
        task_id: Task identifier
        current_status: Status from persisted state
        artifacts_dir: Run directory (published artifact paths are relative to it)
        required_artifacts: List of artifact specs with name/path/min_bytes/sha256
        side_effects: Side effects policy (none/idempotent/unsafe)
        staging_dir: Attempt staging directory for interrupted verification
        require_checksum: Reject artifacts without a matching recorded checksum

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

    # Completed tasks: validate artifacts before reuse
    if current_status == TaskStatus.COMPLETED:
        missing, invalid = _check_artifacts(
            artifacts_dir,
            required_artifacts,
            require_checksum=require_checksum,
        )
        problems = missing + invalid
        if problems:
            if side_effects == "unsafe":
                return TaskReconciliation(
                    task_id=task_id,
                    old_status=current_status,
                    new_status=TaskStatus.BLOCKED,
                    reason=f"Artifacts invalid but side_effects=unsafe: {problems}",
                    safe=False,
                    artifacts_valid=False,
                    missing_artifacts=problems,
                )
            return TaskReconciliation(
                task_id=task_id,
                old_status=current_status,
                new_status=TaskStatus.PENDING,
                reason=f"Artifacts invalid, will re-execute: {problems}",
                safe=True,
                artifacts_valid=False,
                missing_artifacts=problems,
            )

        return TaskReconciliation(
            task_id=task_id,
            old_status=current_status,
            new_status=TaskStatus.COMPLETED,
            reason="Artifacts validated, reusing completed task",
            safe=True,
            artifacts_valid=True,
            reuse=True,
        )

    # Verifying: verification may have passed before publication. Keep the
    # phase so the controller can publish from staging without re-executing.
    if current_status == TaskStatus.VERIFYING:
        if staging_dir is not None:
            missing, invalid = _check_artifacts(
                staging_dir, required_artifacts, require_checksum=False
            )
            problems = missing + invalid
        else:
            problems = ["staging directory not provided"]

        if problems:
            if side_effects == "unsafe":
                return TaskReconciliation(
                    task_id=task_id,
                    old_status=current_status,
                    new_status=TaskStatus.BLOCKED,
                    reason=f"Interrupted during verification, staging invalid: {problems}",
                    safe=False,
                    artifacts_valid=False,
                    missing_artifacts=problems,
                )
            return TaskReconciliation(
                task_id=task_id,
                old_status=current_status,
                new_status=TaskStatus.PENDING,
                reason=f"Interrupted during verification, will restart: {problems}",
                safe=True,
                artifacts_valid=False,
                missing_artifacts=problems,
            )

        return TaskReconciliation(
            task_id=task_id,
            old_status=current_status,
            new_status=TaskStatus.VERIFYING,
            reason="Verification passed, resuming publication from staging",
            safe=True,
            artifacts_valid=True,
            reuse=True,
            resume_phase="publish",
        )

    # Running: interrupted mid-execution
    if current_status == TaskStatus.RUNNING:
        if side_effects == "unsafe":
            return TaskReconciliation(
                task_id=task_id,
                old_status=current_status,
                new_status=TaskStatus.BLOCKED,
                reason="Interrupted during execution, side_effects=unsafe",
                safe=False,
            )
        return TaskReconciliation(
            task_id=task_id,
            old_status=current_status,
            new_status=TaskStatus.PENDING,
            reason="Interrupted during execution, will restart",
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


def _check_artifacts(
    base_dir: Path,
    required_artifacts: list[dict],
    require_checksum: bool,
) -> tuple[list[str], list[str]]:
    """Return (missing, invalid) artifact names for a directory."""
    missing: list[str] = []
    invalid: list[str] = []
    base_resolved = base_dir.resolve()

    for spec in required_artifacts:
        name = spec.get("name", spec.get("path", "?"))
        path = spec.get("path", "")
        artifact_path = (base_dir / path).resolve()

        # Refuse paths that escape the run directory.
        if base_resolved not in artifact_path.parents and artifact_path != base_resolved:
            invalid.append(f"{name} (path escapes run directory)")
            continue

        if not artifact_path.is_file():
            missing.append(name)
            continue

        min_bytes = int(spec.get("min_bytes", 1))
        size = artifact_path.stat().st_size
        if size < min_bytes:
            invalid.append(f"{name} ({size} bytes < {min_bytes})")
            continue

        expected = spec.get("sha256")
        if require_checksum:
            if not expected:
                invalid.append(f"{name} (no recorded checksum)")
            elif _sha256(artifact_path) != expected:
                invalid.append(f"{name} (checksum mismatch)")

    return missing, invalid


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        while chunk := handle.read(65536):
            digest.update(chunk)
    return digest.hexdigest()
