"""Minimal synchronous run controller."""

import json
import shutil
import time
from datetime import datetime, timezone
from pathlib import Path

from graph_engine.artifacts.manager import ArtifactManager
from graph_engine.errors import ArtifactError, ExecutorError
from graph_engine.execution.context import ExecutionContext, RetryFeedback
from graph_engine.execution.result import validate_result
from graph_engine.executors.registry import ExecutorRegistry
from graph_engine.models.enums import (
    ApprovalPoint,
    ApprovalRequirement,
    ErrorCategory,
    ExecutionStatus,
    RunStatus,
    TaskStatus,
)
from graph_engine.models.run import ErrorRecord, RunState, TaskState
from graph_engine.models.workflow import TaskDefinition, WorkflowDefinition
from graph_engine.observability.events import emit_event
from graph_engine.persistence.approval_store import ApprovalStore
from graph_engine.persistence.layout import RunLayout
from graph_engine.persistence.run_store import save_run_state
from graph_engine.scheduler import compute_ready_tasks
from graph_engine.validation.executors import resolve_executor
from graph_engine.verification import VerificationEngine, VerificationStatus
from graph_engine.verification.feedback import build_retry_feedback


class RunController:
    """
    Execute a workflow with mock/real executors.

    Execution is sequential in this MVP. `max_concurrency` is still enforced by
    the readiness computation, and the controller can later dispatch in parallel
    without changing task semantics.
    """

    def __init__(
        self,
        workflow: WorkflowDefinition,
        layout: RunLayout,
        run_state: RunState,
        registry: ExecutorRegistry | None = None,
    ):
        self.workflow = workflow
        self.layout = layout
        self.state = run_state
        self.registry = registry or ExecutorRegistry(workflow)
        self.approvals = ApprovalStore(layout.run_root)
        self.artifacts = ArtifactManager(layout.run_root)
        self.verifier = VerificationEngine(self.registry, self.approvals)

    def run(self) -> RunState:
        """Run until completion, approval pause, or cancellation."""
        if self.state.status in (
            RunStatus.AWAITING_APPROVAL,
            RunStatus.CANCELLED,
            RunStatus.COMPLETED_WITH_BLOCKERS,
        ):
            self.state.status = RunStatus.RUNNING
        self._emit("run_started", run_id=self.state.run_id)

        guard = 10 + sum(
            (
                task.max_retries
                if task.max_retries is not None
                else self.state.max_retries
            )
            + 2
            for task in self.workflow.tasks
        )
        for _ in range(guard):
            if self.layout.cancel_sentinel.exists():
                return self._cancel()

            if self._timeout_exceeded():
                return self._fail_run("run timeout exceeded", ErrorCategory.RUN_TIMEOUT)

            # Resume a task that already passed verification but was waiting
            # for approval to publish.
            for task in self.workflow.tasks:
                task_state = self.state.tasks.get(task.id)
                if task_state and task_state.status == TaskStatus.VERIFYING:
                    self._verify_and_publish(task, task_state)
                    if self.state.status == RunStatus.AWAITING_APPROVAL:
                        return self.state

            approved = self._approved_task_ids()
            rejected = self._rejected_task_ids()
            plan = compute_ready_tasks(
                self.workflow,
                self.state,
                self.state.max_concurrency,
                approved_task_ids=approved,
                rejected_task_ids=rejected,
            )

            for task_id, reason in plan.blocked.items():
                self._set_status(task_id, TaskStatus.BLOCKED, block_reason=reason)

            if plan.awaiting_approval:
                self.state.status = RunStatus.AWAITING_APPROVAL
                self._persist()
                self._emit(
                    "run_awaiting_approval",
                    tasks=plan.awaiting_approval,
                )
                return self.state

            if not plan.ready:
                return self._settle()

            for task_id in plan.ready:
                self._execute_task(task_id)
                if self.state.status == RunStatus.AWAITING_APPROVAL:
                    return self.state

        return self._fail_run(
            "controller iteration limit reached", ErrorCategory.ORCHESTRATION
        )

    # -- task execution -------------------------------------------------

    def _execute_task(self, task_id: str) -> None:
        task = self.workflow.get_task(task_id)
        task_state = self.state.tasks[task_id]

        if task_state.status == TaskStatus.VERIFYING:
            self._verify_and_publish(task, task_state)
            return

        max_attempts = (
            task.max_retries
            if task.max_retries is not None
            else self.state.max_retries
        ) + 1
        attempt = task_state.current_attempt + 1
        task_state.current_attempt = attempt
        self._set_status(task_id, TaskStatus.RUNNING)
        self._emit("task_started", task_id=task_id, attempt=attempt)

        try:
            executor_name = resolve_executor(self.workflow, task_id)
            executor = self.registry.get_executor(executor_name)
        except (ExecutorError, ValueError) as exc:
            self._block(task, task_state, f"executor configuration error: {exc}")
            return

        staging = self.layout.task_staging_dir(task_id, attempt)
        if staging.exists():
            shutil.rmtree(staging)
        staging.mkdir(parents=True, exist_ok=True)

        try:
            context = self._build_context(task, attempt, staging)
        except (ValueError, OSError) as exc:
            self._block(task, task_state, f"cannot build task context: {exc}")
            return

        started = time.monotonic()
        try:
            result = executor.execute(context)
        except Exception as exc:  # noqa: BLE001 - adapter errors become failures
            self.state.active_execution_seconds += int(time.monotonic() - started)
            self._retry_or_block(
                task,
                task_state,
                attempt,
                max_attempts,
                error=f"executor crashed: {type(exc).__name__}: {exc}",
                verification_results=[],
            )
            return

        self.state.active_execution_seconds += int(time.monotonic() - started)

        result_errors = validate_result(result)
        if result_errors:
            self._retry_or_block(
                task,
                task_state,
                attempt,
                max_attempts,
                error="invalid executor result: " + "; ".join(result_errors),
                verification_results=[],
            )
            return

        if result.status != ExecutionStatus.SUCCESS:
            self._retry_or_block(
                task,
                task_state,
                attempt,
                max_attempts,
                error=result.error or f"executor status: {result.status.value}",
                verification_results=[],
            )
            return

        artifact_records = self._validate_outputs(task, staging)
        if artifact_records is None:
            self._retry_or_block(
                task,
                task_state,
                attempt,
                max_attempts,
                error="declared output artifacts are missing or invalid",
                verification_results=[],
            )
            return

        self._set_status(task_id, TaskStatus.VERIFYING)
        self._save_attempt(task, attempt, "verifying", result.summary, [])
        self._verify_and_publish(task, task_state, artifact_records)

    def _verify_and_publish(
        self,
        task: TaskDefinition,
        task_state: TaskState,
        artifact_records: list | None = None,
    ) -> None:
        attempt = max(task_state.current_attempt, 1)
        staging = self.layout.task_staging_dir(task.id, attempt)

        if artifact_records is None:
            artifact_records = self._validate_outputs(task, staging)
            if artifact_records is None:
                self._block(task, task_state, "staged artifacts missing on resume")
                return

        try:
            input_artifacts = self._input_paths(task, staging)
        except ValueError as exc:
            self._block(task, task_state, f"cannot build verification context: {exc}")
            return

        results, passed = self.verifier.verify_all(
            task.verification,
            staging,
            {
                "task_id": task.id,
                "input_artifacts": input_artifacts,
                "required_outputs": {out.name: out.path for out in task.outputs},
            },
        )

        if not passed:
            self._save_attempt(
                task,
                attempt,
                "verification_failed",
                "verification failed",
                [r.message for r in results],
            )
            pending = any(r.status == VerificationStatus.PENDING for r in results)
            if pending:
                self.state.status = RunStatus.AWAITING_APPROVAL
                self._persist()
                self._emit("run_awaiting_approval", tasks=[task.id])
                return

            max_attempts = (
                task.max_retries
                if task.max_retries is not None
                else self.state.max_retries
            ) + 1
            feedback = build_retry_feedback(
                attempt,
                results,
                self._invalid_output_names(task, staging),
            )
            self._retry_or_block(
                task,
                task_state,
                attempt,
                max_attempts,
                error="verification failed",
                verification_results=results,
                feedback=feedback,
            )
            return

        # Approval before publishing the verified result.
        if (
            task.approval == ApprovalRequirement.REQUIRED
            and task.approval_point == ApprovalPoint.BEFORE_PUBLISH
        ):
            if self._is_rejected(task.id):
                self._block(task, task_state, "approval rejected")
                return
            if not self._is_approved(task.id):
                self.state.status = RunStatus.AWAITING_APPROVAL
                self._persist()
                self._emit("run_awaiting_approval", tasks=[task.id])
                return

        try:
            self._publish(task, staging, artifact_records)
        except ArtifactError as exc:
            self._block(task, task_state, f"artifact publication failed: {exc}")
            return

        task_state.artifacts = artifact_records
        task_state.completed_at = _now()
        self._set_status(task.id, TaskStatus.COMPLETED)
        self._save_attempt(task, attempt, "completed", "task completed", [])
        self._emit("task_completed", task_id=task.id, attempt=attempt)

    def _publish(self, task: TaskDefinition, staging: Path, records: list) -> None:
        for record in records:
            staged = staging / record["path"]
            self.artifacts.publish_artifact(staged, record["path"])

    def _invalid_output_names(self, task: TaskDefinition, staging: Path) -> list[str]:
        """Names of declared outputs that are missing or invalid in staging."""
        names = []
        for output in task.outputs:
            try:
                self.artifacts.validate_output(output.path, staging, output.min_bytes)
            except ArtifactError:
                names.append(output.name)
        return names

    def _validate_outputs(self, task: TaskDefinition, staging: Path) -> list | None:
        records = []
        for output in task.outputs:
            try:
                record = self.artifacts.validate_output(
                    output.path, staging, output.min_bytes
                )
            except ArtifactError as exc:
                self._emit("artifact_invalid", task_id=task.id, error=str(exc))
                return None
            records.append(
                {
                    "name": output.name,
                    "path": record.path,
                    "size_bytes": record.size_bytes,
                    "sha256": record.sha256,
                }
            )
        return records

    def _input_paths(self, task: TaskDefinition, staging: Path) -> dict[str, Path]:
        """Map declared input names to their staged paths."""
        paths: dict[str, Path] = {}
        for inp in task.inputs:
            producer = self.workflow.get_task(inp.from_task)
            if producer is None:
                raise ValueError(
                    f"task '{task.id}': input '{inp.name}' references unknown "
                    f"task '{inp.from_task}'"
                )
            output = next((o for o in producer.outputs if o.name == inp.artifact), None)
            if output is None:
                raise ValueError(
                    f"task '{task.id}': input '{inp.name}' references unknown "
                    f"artifact '{inp.artifact}' on '{inp.from_task}'"
                )
            source = self.layout.run_root / output.path
            paths[inp.name] = staging / "inputs" / inp.name / source.name
        return paths

    def _build_context(
        self, task: TaskDefinition, attempt: int, staging: Path
    ) -> ExecutionContext:
        input_artifacts = self._input_paths(task, staging)
        for inp in task.inputs:
            producer = self.workflow.get_task(inp.from_task)
            output = next((o for o in producer.outputs if o.name == inp.artifact), None)
            source = self.layout.run_root / output.path
            self.artifacts.copy_input_artifact(source, staging, inp.name)

        return ExecutionContext(
            task_id=task.id,
            task_type=task.type,
            goal=f"Execute {task.type} task '{task.id}'",
            acceptance_criteria=[
                c.acceptance_criteria or c.id for c in task.verification
            ],
            input_artifacts=input_artifacts,
            required_outputs={out.name: out.path for out in task.outputs},
            staging_dir=staging,
            attempt_number=attempt,
            retry_feedback=self._feedback_for(task, attempt),
            idempotency_key=task.idempotency_key,
        )

    def _feedback_for(self, task: TaskDefinition, attempt: int) -> RetryFeedback | None:
        if attempt <= 1:
            return None
        path = self.layout.task_attempt_file(task.id, attempt - 1)
        if not path.exists():
            return None
        import json

        try:
            data = json.loads(path.read_text())
        except (OSError, ValueError):
            return None
        feedback = data.get("retry_feedback") or {}
        messages = data.get("verification_messages") or [data.get("summary", "")]
        return RetryFeedback(
            previous_attempt=feedback.get("previous_attempt", attempt - 1),
            failures=feedback.get("failures") or [m for m in messages if m],
            reviewer_findings=feedback.get("reviewer_findings"),
            missing_artifacts=feedback.get("missing_artifacts", []),
        )

    # -- retry and terminal states --------------------------------------

    def _retry_or_block(
        self,
        task: TaskDefinition,
        task_state: TaskState,
        attempt: int,
        max_attempts: int,
        error: str,
        verification_results: list,
        feedback: RetryFeedback | None = None,
    ) -> None:
        messages = [r.message for r in verification_results] or [error]
        self._save_attempt(
            task, attempt, "failed", error, messages, feedback=feedback
        )
        if attempt < max_attempts:
            self._set_status(task.id, TaskStatus.RETRYING)
            self._emit("task_retry", task_id=task.id, attempt=attempt, error=error)
        else:
            self._block(task, task_state, f"retry budget exhausted: {error}")

    def _block(self, task: TaskDefinition, task_state: TaskState, reason: str) -> None:
        self._set_status(task.id, TaskStatus.BLOCKED, block_reason=reason)
        self._emit("task_blocked", task_id=task.id, reason=reason)

    def _settle(self) -> RunState:
        statuses = {t.status for t in self.state.tasks.values()}
        if statuses and statuses == {TaskStatus.COMPLETED}:
            self.state.status = RunStatus.COMPLETED
        elif TaskStatus.PENDING in statuses or TaskStatus.RETRYING in statuses:
            self.state.status = RunStatus.FAILED
            self.state.run_errors.append(
                _error("orchestration", "tasks are waiting but none are ready")
            )
        elif statuses & {TaskStatus.BLOCKED, TaskStatus.FAILED}:
            self.state.status = RunStatus.COMPLETED_WITH_BLOCKERS
        else:
            self.state.status = RunStatus.COMPLETED

        self.state.completed_at = _now()
        self._persist()
        self._emit("run_completed", status=self.state.status.value)
        return self.state

    def _cancel(self) -> RunState:
        self.state.status = RunStatus.CANCELLED
        self.state.completed_at = _now()
        self._persist()
        self._emit("run_cancelled")
        return self.state

    def _fail_run(self, reason: str, category: ErrorCategory) -> RunState:
        self.state.status = RunStatus.FAILED
        self.state.run_errors.append(_error(category.value, reason))
        self.state.completed_at = _now()
        self._persist()
        self._emit("run_failed", reason=reason)
        return self.state

    def _timeout_exceeded(self) -> bool:
        limit = self.state.max_run_duration_minutes
        if not limit:
            return False
        return self.state.active_execution_seconds >= limit * 60

    # -- helpers --------------------------------------------------------

    def _approved_task_ids(self) -> frozenset[str]:
        return frozenset(
            task.id for task in self.workflow.tasks if self._is_approved(task.id)
        )

    def _rejected_task_ids(self) -> frozenset[str]:
        return frozenset(
            task.id for task in self.workflow.tasks if self._is_rejected(task.id)
        )

    def _is_approved(self, task_id: str) -> bool:
        decision = self.approvals.get_approval(task_id)
        return bool(decision and decision.get("approved") is True)

    def _is_rejected(self, task_id: str) -> bool:
        decision = self.approvals.get_approval(task_id)
        return bool(decision and decision.get("approved") is False)

    def _set_status(
        self,
        task_id: str,
        status: TaskStatus,
        block_reason: str | None = None,
    ) -> None:
        task_state = self.state.tasks[task_id]
        task_state.status = status
        if block_reason is not None:
            task_state.block_reason = block_reason
        if status == TaskStatus.RUNNING and not task_state.started_at:
            task_state.started_at = _now()
        self._persist()

    def _save_attempt(
        self,
        task: TaskDefinition,
        attempt: int,
        status: str,
        summary: str,
        verification_messages: list[str],
        feedback: RetryFeedback | None = None,
    ) -> None:
        path = self.layout.task_attempt_file(task.id, attempt)
        path.parent.mkdir(parents=True, exist_ok=True)
        import json

        payload = {
            "task_id": task.id,
            "attempt": attempt,
            "status": status,
            "summary": summary,
            "verification_messages": verification_messages,
            "retry_feedback": (
                {
                    "previous_attempt": feedback.previous_attempt,
                    "failures": feedback.failures,
                    "reviewer_findings": feedback.reviewer_findings,
                    "missing_artifacts": feedback.missing_artifacts,
                }
                if feedback
                else None
            ),
            "finished_at": _now(),
        }
        path.write_text(json.dumps(payload, indent=2))

    def _persist(self) -> None:
        save_run_state(self.state, self.layout)

    def _emit(self, event: str, **data) -> None:
        try:
            emit_event(self.layout.events_log, event, data)
        except OSError:
            pass


def _now() -> str:
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).isoformat()


def _error(category: str, message: str):
    from graph_engine.models.enums import ErrorCategory
    from graph_engine.models.run import ErrorRecord

    return ErrorRecord(
        category=ErrorCategory(category),
        message=message,
        timestamp=_now(),
    )
