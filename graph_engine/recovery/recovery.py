"""Recovery manager for resuming workflows."""

import hashlib
import json
from pathlib import Path

from graph_engine.errors import RecoveryError
from graph_engine.models.enums import RunStatus, TaskStatus
from graph_engine.parser import parse_workflow_file
from graph_engine.recovery.reconcile import reconcile_task_status


class RecoveryManager:
    """Manages workflow recovery and resume."""

    def __init__(self, run_dir: Path):
        """
        Initialize recovery manager.

        Args:
            run_dir: Run directory to recover
        """
        self.run_dir = run_dir

    def can_resume(self) -> tuple[bool, str | None]:
        """
        Check if run can be resumed.

        Returns:
            (can_resume, reason) tuple
        """
        # Check run.json exists
        run_json = self.run_dir / "run.json"
        if not run_json.exists():
            return (False, "run.json not found")

        # Load run state
        try:
            with open(run_json) as f:
                run_state = json.load(f)
        except (OSError, json.JSONDecodeError) as e:
            return (False, f"Cannot read run.json: {e}")

        # Check workflow snapshot
        workflow_snapshot = self.run_dir / "workflow.yaml"
        if not workflow_snapshot.exists():
            return (False, "workflow.yaml snapshot not found")

        # Check status
        status = run_state.get("status")
        if status == RunStatus.COMPLETED.value:
            return (False, "Run already completed")

        # Resumable statuses
        resumable = {
            RunStatus.RUNNING.value,
            RunStatus.AWAITING_APPROVAL.value,
            RunStatus.COMPLETED_WITH_BLOCKERS.value,
            RunStatus.CANCELLED.value,
        }

        if status not in resumable:
            return (False, f"Cannot resume from status: {status}")

        return (True, None)

    def validate_snapshot(
        self,
        expected_hash: str | None = None,
        allow_config_change: bool = False,
    ) -> tuple[bool, str | None]:
        """
        Validate workflow snapshot immutability.

        Args:
            expected_hash: Expected workflow hash (from run.json)
            allow_config_change: Allow executor config changes

        Returns:
            (valid, reason) tuple
        """
        workflow_snapshot = self.run_dir / "workflow.yaml"

        if not workflow_snapshot.exists():
            return (False, "Workflow snapshot not found")

        if expected_hash:
            # Compute current hash
            content = workflow_snapshot.read_bytes()
            current_hash = hashlib.sha256(content).hexdigest()

            if current_hash != expected_hash:
                return (
                    False,
                    f"Workflow hash mismatch: expected {expected_hash[:8]}..., got {current_hash[:8]}...",
                )

        # TODO: Validate executor config hash if needed
        # For now, we trust the snapshot

        return (True, None)

    def create_recovery_plan(
        self,
        workflow,
        run_state: dict,
    ) -> dict:
        """
        Create recovery plan for tasks.

        Args:
            workflow: Parsed workflow definition
            run_state: Current run state from run.json

        Returns:
            Recovery plan dict with task reconciliations
        """
        task_states = run_state.get("tasks", {})
        artifacts_dir = self.run_dir / "artifacts"

        reconciliations = []
        unsafe_tasks = []

        # Build task map for artifact specs
        task_map = {task.id: task for task in workflow.tasks}

        for task_id, status_str in task_states.items():
            if task_id not in task_map:
                # Task no longer in workflow?
                reconciliations.append(
                    {
                        "task_id": task_id,
                        "old_status": status_str,
                        "new_status": TaskStatus.BLOCKED.value,
                        "reason": "Task not found in workflow",
                        "safe": False,
                    }
                )
                unsafe_tasks.append(task_id)
                continue

            task = task_map[task_id]
            current_status = TaskStatus(status_str)

            # Get task side effects policy
            side_effects = getattr(task, "side_effects", "none")

            # Reconcile
            reconciliation = reconcile_task_status(
                task_id=task_id,
                current_status=current_status,
                artifacts_dir=self.run_dir,
                required_artifacts=[
                    {"name": out.name, "path": out.path} for out in task.outputs
                ],
                side_effects=side_effects,
            )

            reconciliations.append(
                {
                    "task_id": reconciliation.task_id,
                    "old_status": reconciliation.old_status.value,
                    "new_status": reconciliation.new_status.value,
                    "reason": reconciliation.reason,
                    "safe": reconciliation.safe,
                    "reuse": reconciliation.reuse,
                }
            )

            if not reconciliation.safe:
                unsafe_tasks.append(task_id)

        return {
            "reconciliations": reconciliations,
            "unsafe_tasks": unsafe_tasks,
            "can_proceed": len(unsafe_tasks) == 0,
        }

    def apply_recovery_plan(
        self,
        run_state: dict,
        recovery_plan: dict,
    ) -> dict:
        """
        Apply recovery plan to run state.

        Args:
            run_state: Current run state
            recovery_plan: Recovery plan from create_recovery_plan

        Returns:
            Updated run state
        """
        # Apply task status changes
        for recon in recovery_plan["reconciliations"]:
            task_id = recon["task_id"]
            run_state["tasks"][task_id] = recon["new_status"]

        # Update run status if needed
        if run_state["status"] == RunStatus.CANCELLED.value:
            # Cancelled run becomes running again
            run_state["status"] = RunStatus.RUNNING.value
        elif run_state["status"] == RunStatus.AWAITING_APPROVAL.value:
            # Keep awaiting approval
            pass
        else:
            # Running or completed_with_blockers -> running
            run_state["status"] = RunStatus.RUNNING.value

        return run_state

    def resume_workflow(
        self,
        allow_config_change: bool = False,
    ) -> dict:
        """
        Resume workflow execution.

        Args:
            allow_config_change: Allow executor config changes

        Returns:
            Recovery info dict

        Raises:
            RecoveryError: If resume is not safe
        """
        # Check if can resume
        can_resume, reason = self.can_resume()
        if not can_resume:
            raise RecoveryError(f"Cannot resume: {reason}")

        # Load run state
        run_json = self.run_dir / "run.json"
        with open(run_json) as f:
            run_state = json.load(f)

        # Validate snapshot
        expected_hash = run_state.get("workflow_hash")
        valid, reason = self.validate_snapshot(
            expected_hash=expected_hash,
            allow_config_change=allow_config_change,
        )
        if not valid:
            raise RecoveryError(f"Snapshot validation failed: {reason}")

        # Load workflow
        workflow_snapshot = self.run_dir / "workflow.yaml"
        workflow, _ = parse_workflow_file(workflow_snapshot)

        # Create recovery plan
        recovery_plan = self.create_recovery_plan(workflow, run_state)

        if not recovery_plan["can_proceed"]:
            unsafe_tasks = recovery_plan["unsafe_tasks"]
            raise RecoveryError(
                f"Unsafe recovery: tasks {unsafe_tasks} require human intervention"
            )

        # Apply plan (in-memory, caller will persist)
        updated_state = self.apply_recovery_plan(run_state, recovery_plan)

        return {
            "recovery_plan": recovery_plan,
            "updated_state": updated_state,
            "workflow": workflow,
        }
