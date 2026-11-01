"""Tests for recovery manager using real run state."""

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
