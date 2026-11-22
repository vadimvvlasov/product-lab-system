"""Recovery manager for resuming workflows."""

import json
from pathlib import Path

from graph_engine.errors import RecoveryError
from graph_engine.models.enums import RunStatus, TaskStatus
from graph_engine.models.run import RunState, TaskState
from graph_engine.parser import parse_workflow_file
from graph_engine.persistence.snapshot import verify_snapshot_hash
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
        run_json = self.run_dir / "run.json"
        if not run_json.exists():
            return (False, "run.json not found")

        try:
            with open(run_json) as f:
                run_state = json.load(f)
        except (OSError, json.JSONDecodeError) as e:
            return (False, f"Cannot read run.json: {e}")

        workflow_snapshot = self.run_dir / "workflow.yaml"
        if not workflow_snapshot.exists():
            return (False, "workflow.yaml snapshot not found")

        status = run_state.get("status")
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
        expected_config_hash: str | None = None,
    ) -> tuple[bool, str | None]:
        """
        Validate workflow snapshot immutability.

        Args:
            expected_hash: Expected workflow hash (from run.json)
            allow_config_change: Allow executor config changes
            expected_config_hash: Expected executor config hash (from run.json)

        Returns:
            (valid, reason) tuple
        """
        workflow_snapshot = self.run_dir / "workflow.yaml"

        if not workflow_snapshot.exists():
            return (False, "Workflow snapshot not found")

        if expected_hash and not verify_snapshot_hash(workflow_snapshot, expected_hash):
            return (False, "Workflow hash mismatch: snapshot was modified")

        if not allow_config_change and expected_config_hash:
            config_snapshot = self.run_dir / "executor_config.json"
            if not config_snapshot.exists():
                return (False, "Executor config snapshot not found")
            if not verify_snapshot_hash(config_snapshot, expected_config_hash):
                return (False, "Executor config hash mismatch: snapshot was modified")

        return (True, None)

    def create_recovery_plan(
        self,
        workflow,
        run_state: RunState,
    ) -> dict:
        """
        Create recovery plan for tasks.

        Args:
            workflow: Parsed workflow definition
            run_state: Current run state

        Returns:
            Recovery plan dict with task reconciliations
        """
        artifacts_dir = self.run_dir / "artifacts"
        task_map = {task.id: task for task in workflow.tasks}

        reconciliations = []
        unsafe_tasks = []

        for task_id, task_state in run_state.tasks.items():
            if task_id not in task_map:
                reconciliations.append(
                    {
                        "task_id": task_id,
                        "old_status": task_state.status.value,
                        "new_status": TaskStatus.BLOCKED.value,
                        "reason": "Task not found in workflow",
                        "safe": False,
                        "reuse": False,
                        "resume_phase": None,
                    }
                )
                unsafe_tasks.append(task_id)
                continue

            task = task_map[task_id]
            staging_dir = None
            if task_state.current_attempt > 0:
                staging_dir = (
                    artifacts_dir
                    / ".staging"
                    / task_id
                    / f"attempt-{task_state.current_attempt:03d}"
                )

            recorded = {
                record.get("path"): record for record in task_state.artifacts
            }
            required_artifacts = []
            for out in task.outputs:
                spec = {
                    "name": out.name,
                    "path": out.path,
                    "min_bytes": out.min_bytes,
                }
                record = recorded.get(out.path)
                if record and record.get("sha256"):
                    spec["sha256"] = record["sha256"]
                required_artifacts.append(spec)

            reconciliation = reconcile_task_status(
                task_id=task_id,
                current_status=task_state.status,
                artifacts_dir=self.run_dir,
                required_artifacts=required_artifacts,
                side_effects=task.side_effects.value,
                staging_dir=staging_dir,
                require_checksum=task_state.status == TaskStatus.COMPLETED,
            )

            reconciliations.append(
                {
                    "task_id": reconciliation.task_id,
                    "old_status": reconciliation.old_status.value,
                    "new_status": reconciliation.new_status.value,
                    "reason": reconciliation.reason,
                    "safe": reconciliation.safe,
                    "reuse": reconciliation.reuse,
                    "resume_phase": reconciliation.resume_phase,
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
        run_state: RunState,
        recovery_plan: dict,
    ) -> RunState:
        """
        Apply recovery plan to run state.

        Args:
            run_state: Current run state
            recovery_plan: Recovery plan from create_recovery_plan

        Returns:
            Updated run state
        """
        for recon in recovery_plan["reconciliations"]:
            task_id = recon["task_id"]
            new_status = TaskStatus(recon["new_status"])
            task_state = run_state.tasks.get(task_id)
            if task_state is None:
                task_state = TaskState(task_id=task_id, status=new_status)
                run_state.tasks[task_id] = task_state
            task_state.status = new_status
            if new_status == TaskStatus.BLOCKED:
                task_state.block_reason = recon["reason"]
            elif new_status in (TaskStatus.PENDING, TaskStatus.RETRYING):
                task_state.block_reason = None

        if run_state.status in (
            RunStatus.CANCELLED,
            RunStatus.AWAITING_APPROVAL,
            RunStatus.COMPLETED_WITH_BLOCKERS,
        ):
            run_state.status = RunStatus.RUNNING

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
            Recovery info dict with recovery_plan, updated_state (RunState), workflow

        Raises:
            RecoveryError: If resume is not safe
        """
        can_resume, reason = self.can_resume()
        if not can_resume:
            raise RecoveryError(f"Cannot resume: {reason}")

        run_json = self.run_dir / "run.json"
        try:
            with open(run_json) as f:
                run_state = RunState.from_dict(json.load(f))
        except (OSError, json.JSONDecodeError, ValueError, TypeError) as e:
            raise RecoveryError(f"Cannot load run state: {e}") from e

        valid, reason = self.validate_snapshot(
            expected_hash=run_state.workflow_snapshot_hash,
            allow_config_change=allow_config_change,
            expected_config_hash=run_state.executor_config_hash,
        )
        if not valid:
            raise RecoveryError(f"Snapshot validation failed: {reason}")

        workflow_snapshot = self.run_dir / "workflow.yaml"
        workflow, _ = parse_workflow_file(workflow_snapshot)

        recovery_plan = self.create_recovery_plan(workflow, run_state)

        if not recovery_plan["can_proceed"]:
            unsafe_tasks = recovery_plan["unsafe_tasks"]
            raise RecoveryError(
                f"Unsafe recovery: tasks {unsafe_tasks} require human intervention"
            )

        updated_state = self.apply_recovery_plan(run_state, recovery_plan)

        return {
            "recovery_plan": recovery_plan,
            "updated_state": updated_state,
            "workflow": workflow,
        }
