"""Tests for recovery manager using real run state."""

import hashlib
import json

import pytest

from graph_engine.errors import RecoveryError
from graph_engine.models.enums import RunStatus, TaskStatus
from graph_engine.models.run import RunState
from graph_engine.parser import parse_workflow
from graph_engine.persistence.run_store import create_run, save_run_state
from graph_engine.recovery.recovery import RecoveryManager

WORKFLOW = """version: "1"
workflow:
  id: test-workflow
  description: Test
execution:
  max_concurrency: 1
  max_retries: 1
executors:
  mock:
    adapter: mock
    config: {}
executor_mapping:
  test: mock
tasks:
  - id: task1
    type: test
    outputs:
      - name: output1
        path: artifacts/output1.txt
    verification:
      - id: test
        method: command
        command: "test -f artifacts/output1.txt"
"""

UNSAFE_WORKFLOW = """version: "1"
workflow:
  id: unsafe-workflow
  description: Unsafe workflow
execution:
  max_concurrency: 1
  max_retries: 1
executors:
  mock:
    adapter: mock
    config: {}
executor_mapping:
  deploy: mock
tasks:
  - id: deploy
    type: deploy
    side_effects: unsafe
    idempotency_key: deploy-key
    outputs: []
    verification:
      - id: test
        method: command
        command: "true"
"""

RUN_ID = "test-workflow-20261031T210000Z-abcdef"


def make_run(
    tmp_path,
    workflow_yaml=WORKFLOW,
    status=RunStatus.RUNNING,
    task_status=TaskStatus.PENDING,
    artifact=False,
    attempt=0,
    run_id=RUN_ID,
):
    workflow = parse_workflow(workflow_yaml.encode())
    state, layout = create_run(
        workflow, workflow_yaml.encode(), tmp_path / "runs", run_id=run_id
    )
    state.status = status
    task = next(iter(state.tasks.values()))
    task.status = task_status
    task.current_attempt = attempt

    if artifact:
        target = layout.run_root / "artifacts" / "output1.txt"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("output content")
        task.artifacts = [
            {
                "name": "output1",
                "path": "artifacts/output1.txt",
                "size_bytes": target.stat().st_size,
                "sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
            }
        ]

    save_run_state(state, layout)
    return RecoveryManager(layout.run_root), state, layout


def test_can_resume_running(tmp_path):
    manager, _, _ = make_run(tmp_path)
    can_resume, reason = manager.can_resume()

    assert can_resume is True
    assert reason is None


def test_cannot_resume_completed(tmp_path):
    manager, _, _ = make_run(tmp_path, status=RunStatus.COMPLETED)
    can_resume, reason = manager.can_resume()

    assert can_resume is False
    assert "cannot resume from status" in reason.lower()


def test_can_resume_awaiting_approval(tmp_path):
    manager, _, _ = make_run(tmp_path, status=RunStatus.AWAITING_APPROVAL)
    can_resume, _ = manager.can_resume()

    assert can_resume is True


def test_can_resume_cancelled(tmp_path):
    manager, _, _ = make_run(tmp_path, status=RunStatus.CANCELLED)
    can_resume, _ = manager.can_resume()

    assert can_resume is True


def test_validate_snapshot_hash_match(tmp_path):
    _, state, layout = make_run(tmp_path)
    manager = RecoveryManager(layout.run_root)

    valid, reason = manager.validate_snapshot(expected_hash=state.workflow_snapshot_hash)

    assert valid is True
    assert reason is None


def test_validate_snapshot_hash_mismatch(tmp_path):
    _, state, layout = make_run(tmp_path)
    manager = RecoveryManager(layout.run_root)
    (layout.run_root / "workflow.yaml").write_text("changed content")

    valid, reason = manager.validate_snapshot(expected_hash=state.workflow_snapshot_hash)

    assert valid is False
    assert "mismatch" in reason.lower()


def test_validate_snapshot_missing(tmp_path):
    _, _, layout = make_run(tmp_path)
    (layout.run_root / "workflow.yaml").unlink()

    valid, reason = RecoveryManager(layout.run_root).validate_snapshot()

    assert valid is False
    assert "not found" in reason.lower()


def test_resume_workflow_with_completed_task(tmp_path):
    manager, _, _ = make_run(
        tmp_path, task_status=TaskStatus.COMPLETED, artifact=True, attempt=1
    )

    info = manager.resume_workflow()

    assert info["recovery_plan"]["can_proceed"] is True
    recon = info["recovery_plan"]["reconciliations"][0]
    assert recon["new_status"] == TaskStatus.COMPLETED.value
    assert recon["reuse"] is True
    assert isinstance(info["updated_state"], RunState)


def test_resume_workflow_with_missing_artifacts(tmp_path):
    manager, _, _ = make_run(
        tmp_path, task_status=TaskStatus.COMPLETED, artifact=False, attempt=1
    )

    info = manager.resume_workflow()

    recon = info["recovery_plan"]["reconciliations"][0]
    assert recon["new_status"] == TaskStatus.PENDING.value
    assert recon["reuse"] is False


def test_resume_workflow_with_zero_byte_artifact_reexecutes(tmp_path):
    manager, _, layout = make_run(
        tmp_path, task_status=TaskStatus.COMPLETED, attempt=1
    )
    target = layout.run_root / "artifacts" / "output1.txt"
    target.write_text("")

    info = manager.resume_workflow()

    recon = info["recovery_plan"]["reconciliations"][0]
    assert recon["new_status"] == TaskStatus.PENDING.value


def test_resume_workflow_unsafe_task_blocks(tmp_path):
    manager, _, _ = make_run(
        tmp_path,
        workflow_yaml=UNSAFE_WORKFLOW,
        task_status=TaskStatus.RUNNING,
        run_id="unsafe-workflow-20261031T210000Z-abcdef",
    )

    with pytest.raises(RecoveryError) as exc_info:
        manager.resume_workflow()

    assert "unsafe recovery" in str(exc_info.value).lower()


def test_resume_workflow_cancelled_becomes_running(tmp_path):
    manager, _, _ = make_run(tmp_path, status=RunStatus.CANCELLED)

    info = manager.resume_workflow()

    assert info["updated_state"].status == RunStatus.RUNNING


def test_resume_workflow_verifying_resumes_publish(tmp_path):
    manager, _, layout = make_run(
        tmp_path, task_status=TaskStatus.VERIFYING, attempt=1
    )
    staging = layout.run_root / "artifacts" / ".staging" / "task1" / "attempt-001"
    (staging / "artifacts").mkdir(parents=True)
    (staging / "artifacts" / "output1.txt").write_text("staged content")

    info = manager.resume_workflow()

    recon = info["recovery_plan"]["reconciliations"][0]
    assert recon["new_status"] == TaskStatus.VERIFYING.value
    assert recon["resume_phase"] == "publish"


def test_applied_state_roundtrips(tmp_path):
    manager, _, _ = make_run(tmp_path, status=RunStatus.CANCELLED)

    info = manager.resume_workflow()
    reloaded = RunState.from_dict(info["updated_state"].to_dict())

    assert reloaded.status == RunStatus.RUNNING
    assert reloaded.tasks["task1"].status == TaskStatus.PENDING


def test_cannot_resume_missing_run_json(tmp_path):
    manager = RecoveryManager(tmp_path)
    can_resume, reason = manager.can_resume()

    assert can_resume is False
    assert "not found" in reason.lower()


def test_cannot_resume_corrupted_run_json(tmp_path):
    (tmp_path / "run.json").write_text("invalid json {")
    (tmp_path / "workflow.yaml").write_text(WORKFLOW)

    can_resume, reason = RecoveryManager(tmp_path).can_resume()

    assert can_resume is False
    assert "cannot read" in reason.lower()


def test_resume_workflow_hash_mismatch_fails(tmp_path):
    manager, _, layout = make_run(tmp_path)
    (layout.run_root / "workflow.yaml").write_text(WORKFLOW + "\n# tampered\n")
    with pytest.raises(RecoveryError) as exc_info:
        manager.resume_workflow()

    assert "snapshot validation failed" in str(exc_info.value).lower()


def test_resume_workflow_tampered_artifact_reexecutes(tmp_path):
    manager, _, layout = make_run(
        tmp_path, task_status=TaskStatus.COMPLETED, artifact=True, attempt=1
    )
    (layout.run_root / "artifacts" / "output1.txt").write_text("tampered content")

    info = manager.resume_workflow()

    recon = info["recovery_plan"]["reconciliations"][0]
    assert recon["new_status"] == TaskStatus.PENDING.value
    assert "checksum mismatch" in recon["reason"].lower()


def test_resume_workflow_without_recorded_checksum_reexecutes(tmp_path):
    manager, state, layout = make_run(
        tmp_path, task_status=TaskStatus.COMPLETED, artifact=True, attempt=1
    )
    state.tasks["task1"].artifacts = []
    save_run_state(state, layout)

    info = manager.resume_workflow()

    recon = info["recovery_plan"]["reconciliations"][0]
    assert recon["new_status"] == TaskStatus.PENDING.value
    assert "no recorded checksum" in recon["reason"].lower()


CHAIN_WORKFLOW = """version: "1"
workflow:
  id: chain-workflow
  description: Chain
execution:
  max_concurrency: 1
  max_retries: 0
executors:
  mock:
    adapter: mock
    config: {{}}
executor_mapping:
  test: mock
tasks:
  - id: a
    type: test
    outputs:
      - name: out
        path: artifacts/a.txt
    verification:
      - id: v
        method: command
        command: "test -f artifacts/a.txt"
  - id: b
    type: test
{b_extra}
    depends_on: [a]
    inputs:
      - name: data
        from: a
        artifact: out
    outputs:
      - name: out
        path: artifacts/b.txt
    verification:
      - id: v
        method: command
        command: "test -f artifacts/b.txt"
  - id: c
    type: test
    depends_on: [b]
    outputs:
      - name: out
        path: artifacts/c.txt
    verification:
      - id: v
        method: command
        command: "test -f artifacts/c.txt"
  - id: d
    type: test
    outputs:
      - name: out
        path: artifacts/d.txt
    verification:
      - id: v
        method: command
        command: "test -f artifacts/d.txt"
"""

CHAIN_RUN_ID = "chain-workflow-20261031T210000Z-abcdef"


def make_chain_run(tmp_path, b_extra="", delete_a=True):
    yaml_text = CHAIN_WORKFLOW.format(b_extra=b_extra)
    workflow = parse_workflow(yaml_text.encode())
    state, layout = create_run(
        workflow, yaml_text.encode(), tmp_path / "runs", run_id=CHAIN_RUN_ID
    )
    state.status = RunStatus.RUNNING
    for task_id in ("a", "b", "c", "d"):
        target = layout.run_root / "artifacts" / f"{task_id}.txt"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(f"{task_id} content")
        task_state = state.tasks[task_id]
        task_state.status = TaskStatus.COMPLETED
        task_state.current_attempt = 1
        task_state.completed_at = "2026-10-31T21:00:00+00:00"
        task_state.artifacts = [
            {
                "name": "out",
                "path": f"artifacts/{task_id}.txt",
                "size_bytes": target.stat().st_size,
                "sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
            }
        ]
    if delete_a:
        (layout.run_root / "artifacts" / "a.txt").unlink()
    save_run_state(state, layout)
    return workflow, state, layout, RecoveryManager(layout.run_root)


def _by_id(plan):
    return {r["task_id"]: r for r in plan["reconciliations"]}


def test_recovery_resets_completed_downstream_of_reset_upstream(tmp_path):
    workflow, state, layout, manager = make_chain_run(tmp_path)

    plan = manager.create_recovery_plan(workflow, state)
    recon = _by_id(plan)

    assert recon["a"]["new_status"] == "pending"
    # direct dependent (depends_on and inputs.from) is reset
    assert recon["b"]["new_status"] == "pending"
    assert recon["b"]["reuse"] is False
    assert recon["b"]["safe"] is True
    assert "'a'" in recon["b"]["reason"]
    # transitive: grandchild reset too
    assert recon["c"]["new_status"] == "pending"
    assert recon["c"]["reuse"] is False
    assert "'b'" in recon["c"]["reason"]
    # independent branch stays reused
    assert recon["d"]["new_status"] == "completed"
    assert recon["d"]["reuse"] is True
    assert plan["can_proceed"] is True


def test_recovery_unsafe_downstream_blocks(tmp_path):
    workflow, state, layout, manager = make_chain_run(
        tmp_path,
        b_extra="    side_effects: unsafe\n    idempotency_key: b-key",
    )

    plan = manager.create_recovery_plan(workflow, state)
    recon = _by_id(plan)

    assert recon["b"]["new_status"] == "blocked"
    assert recon["b"]["safe"] is False
    assert "b" in plan["unsafe_tasks"]
    assert plan["can_proceed"] is False


def test_recovery_apply_clears_artifacts_and_keeps_files(tmp_path):
    workflow, state, layout, manager = make_chain_run(tmp_path)

    plan = manager.create_recovery_plan(workflow, state)
    manager.apply_recovery_plan(state, plan)

    for task_id in ("a", "b", "c"):
        assert state.tasks[task_id].status == TaskStatus.PENDING
        assert state.tasks[task_id].artifacts == []
        assert state.tasks[task_id].completed_at is None
    assert state.tasks["d"].status == TaskStatus.COMPLETED
    assert state.tasks["d"].artifacts
    # published files are not deleted
    assert (layout.run_root / "artifacts" / "b.txt").exists()
    assert (layout.run_root / "artifacts" / "c.txt").exists()


def test_resume_through_controller_reexecutes_downstream(tmp_path):
    from graph_engine.execution.controller import RunController
    from graph_engine.execution.result import ExecutionResult
    from graph_engine.models.enums import ExecutionStatus

    workflow, state, layout, manager = make_chain_run(tmp_path)
    resumed = manager.resume_workflow()["updated_state"]

    class Executor:
        name = "mock"
        adapter = "test"

        def __init__(self):
            self.tasks = []

        def execute(self, context):
            self.tasks.append(context.task_id)
            for path in context.required_outputs.values():
                target = context.staging_dir / path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text("regenerated")
            return ExecutionResult(status=ExecutionStatus.SUCCESS, summary="ok")

        def cancel(self):
            pass

    executor = Executor()

    class Registry:
        def get_executor(self, name):
            return executor

    result = RunController(workflow, layout, resumed, Registry()).run()

    assert result.status == RunStatus.COMPLETED
    assert executor.tasks == ["a", "b", "c"]
    assert (layout.run_root / "artifacts" / "b.txt").read_text() == "regenerated"
    assert result.tasks["d"].status == TaskStatus.COMPLETED
