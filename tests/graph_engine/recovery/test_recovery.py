"""Tests for recovery manager."""

import hashlib
import json

import pytest

from graph_engine.errors import RecoveryError
from graph_engine.models.enums import RunStatus, TaskStatus
from graph_engine.recovery.recovery import RecoveryManager


@pytest.fixture
def run_dir(tmp_path):
    """Create run directory with basic structure."""
    run_dir = tmp_path / "run-123"
    run_dir.mkdir()
    (run_dir / "artifacts").mkdir()
    return run_dir


@pytest.fixture
def workflow_yaml(run_dir):
    """Create workflow snapshot."""
    content = """version: "1"
workflow:
  id: test-workflow
  description: Test
execution:
  max_concurrency: 1
  max_retries: 1
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
    workflow_path = run_dir / "workflow.yaml"
    workflow_path.write_text(content)

    # Compute hash
    workflow_hash = hashlib.sha256(content.encode()).hexdigest()

    return workflow_path, workflow_hash


def test_can_resume_running(run_dir, workflow_yaml):
    """Test can resume running workflow."""
    _, workflow_hash = workflow_yaml

    run_json = {
        "run_id": "run-123",
        "status": RunStatus.RUNNING.value,
        "workflow_hash": workflow_hash,
        "tasks": {
            "task1": TaskStatus.PENDING.value,
        },
    }

    (run_dir / "run.json").write_text(json.dumps(run_json))

    manager = RecoveryManager(run_dir)
    can_resume, reason = manager.can_resume()

    assert can_resume is True
    assert reason is None


def test_cannot_resume_completed(run_dir, workflow_yaml):
    """Test cannot resume completed workflow."""
    _, workflow_hash = workflow_yaml

    run_json = {
        "run_id": "run-123",
        "status": RunStatus.COMPLETED.value,
        "workflow_hash": workflow_hash,
        "tasks": {},
    }

    (run_dir / "run.json").write_text(json.dumps(run_json))

    manager = RecoveryManager(run_dir)
    can_resume, reason = manager.can_resume()

    assert can_resume is False
    assert "already completed" in reason.lower()


def test_can_resume_awaiting_approval(run_dir, workflow_yaml):
    """Test can resume workflow awaiting approval."""
    _, workflow_hash = workflow_yaml

    run_json = {
        "run_id": "run-123",
        "status": RunStatus.AWAITING_APPROVAL.value,
        "workflow_hash": workflow_hash,
        "tasks": {
            "task1": TaskStatus.VERIFYING.value,
        },
    }

    (run_dir / "run.json").write_text(json.dumps(run_json))

    manager = RecoveryManager(run_dir)
    can_resume, reason = manager.can_resume()

    assert can_resume is True


def test_can_resume_cancelled(run_dir, workflow_yaml):
    """Test can resume cancelled workflow."""
    _, workflow_hash = workflow_yaml

    run_json = {
        "run_id": "run-123",
        "status": RunStatus.CANCELLED.value,
        "workflow_hash": workflow_hash,
        "tasks": {
            "task1": TaskStatus.BLOCKED.value,
        },
    }

    (run_dir / "run.json").write_text(json.dumps(run_json))

    manager = RecoveryManager(run_dir)
    can_resume, reason = manager.can_resume()

    assert can_resume is True


def test_validate_snapshot_hash_match(run_dir, workflow_yaml):
    """Test snapshot validation with matching hash."""
    _, workflow_hash = workflow_yaml

    manager = RecoveryManager(run_dir)
    valid, reason = manager.validate_snapshot(expected_hash=workflow_hash)

    assert valid is True
    assert reason is None


def test_validate_snapshot_hash_mismatch(run_dir, workflow_yaml):
    """Test snapshot validation with mismatched hash."""
    _, workflow_hash = workflow_yaml

    # Change workflow content
    (run_dir / "workflow.yaml").write_text("changed content")

    manager = RecoveryManager(run_dir)
    valid, reason = manager.validate_snapshot(expected_hash=workflow_hash)

    assert valid is False
    assert "mismatch" in reason.lower()


def test_validate_snapshot_missing(run_dir):
    """Test snapshot validation when file is missing."""
    # Don't create workflow.yaml

    manager = RecoveryManager(run_dir)
    valid, reason = manager.validate_snapshot()

    assert valid is False
    assert "not found" in reason.lower()


def test_resume_workflow_with_completed_task(run_dir, workflow_yaml):
    """Test resume with completed task that has valid artifacts."""
    _, workflow_hash = workflow_yaml

    # Create artifact
    output_file = run_dir / "artifacts" / "output1.txt"
    output_file.write_text("output content")

    run_json = {
        "run_id": "run-123",
        "status": RunStatus.RUNNING.value,
        "workflow_hash": workflow_hash,
        "tasks": {
            "task1": TaskStatus.COMPLETED.value,
        },
    }

    (run_dir / "run.json").write_text(json.dumps(run_json))

    manager = RecoveryManager(run_dir)
    recovery_info = manager.resume_workflow()

    # Should reuse completed task
    plan = recovery_info["recovery_plan"]
    assert plan["can_proceed"] is True

    task1_recon = [r for r in plan["reconciliations"] if r["task_id"] == "task1"][0]
    assert task1_recon["new_status"] == TaskStatus.COMPLETED.value
    assert task1_recon["reuse"] is True


def test_resume_workflow_with_missing_artifacts(run_dir, workflow_yaml):
    """Test resume with completed task missing artifacts."""
    _, workflow_hash = workflow_yaml

    # Don't create artifact

    run_json = {
        "run_id": "run-123",
        "status": RunStatus.RUNNING.value,
        "workflow_hash": workflow_hash,
        "tasks": {
            "task1": TaskStatus.COMPLETED.value,
        },
    }

    (run_dir / "run.json").write_text(json.dumps(run_json))

    manager = RecoveryManager(run_dir)
    recovery_info = manager.resume_workflow()

    # Should reset to pending
    plan = recovery_info["recovery_plan"]
    assert plan["can_proceed"] is True

    task1_recon = [r for r in plan["reconciliations"] if r["task_id"] == "task1"][0]
    assert task1_recon["new_status"] == TaskStatus.PENDING.value


def test_resume_workflow_unsafe_task_blocks(run_dir):
    """Test resume fails with unsafe interrupted task."""
    # Workflow with unsafe side effects
    workflow_content = """version: "1"
workflow:
  id: test-workflow
  description: Unsafe workflow
execution:
  max_concurrency: 1
  max_retries: 1
tasks:
  - id: deploy
    type: deploy
    side_effects: unsafe
    outputs: []
    verification:
      - id: test
        method: command
        command: "true"
"""
    workflow_path = run_dir / "workflow.yaml"
    workflow_path.write_text(workflow_content)
    workflow_hash = hashlib.sha256(workflow_content.encode()).hexdigest()

    run_json = {
        "run_id": "run-123",
        "status": RunStatus.RUNNING.value,
        "workflow_hash": workflow_hash,
        "tasks": {
            "deploy": TaskStatus.RUNNING.value,  # Interrupted during running
        },
    }

    (run_dir / "run.json").write_text(json.dumps(run_json))

    manager = RecoveryManager(run_dir)

    with pytest.raises(RecoveryError) as exc_info:
        manager.resume_workflow()

    assert "unsafe recovery" in str(exc_info.value).lower()


def test_resume_workflow_cancelled_becomes_running(run_dir, workflow_yaml):
    """Test cancelled run becomes running after resume."""
    _, workflow_hash = workflow_yaml

    run_json = {
        "run_id": "run-123",
        "status": RunStatus.CANCELLED.value,
        "workflow_hash": workflow_hash,
        "tasks": {
            "task1": TaskStatus.PENDING.value,
        },
    }

    (run_dir / "run.json").write_text(json.dumps(run_json))

    manager = RecoveryManager(run_dir)
    recovery_info = manager.resume_workflow()

    updated_state = recovery_info["updated_state"]
    assert updated_state["status"] == RunStatus.RUNNING.value


def test_cannot_resume_missing_run_json(run_dir):
    """Test cannot resume without run.json."""
    manager = RecoveryManager(run_dir)
    can_resume, reason = manager.can_resume()

    assert can_resume is False
    assert "not found" in reason.lower()


def test_cannot_resume_corrupted_run_json(run_dir):
    """Test cannot resume with corrupted run.json."""
    (run_dir / "run.json").write_text("invalid json {")

    manager = RecoveryManager(run_dir)
    can_resume, reason = manager.can_resume()

    assert can_resume is False
    assert "cannot read" in reason.lower()


def test_resume_workflow_hash_mismatch_fails(run_dir, workflow_yaml):
    """Test resume fails when workflow hash mismatches."""
    _, original_hash = workflow_yaml

    # Use different hash in run.json
    run_json = {
        "run_id": "run-123",
        "status": RunStatus.RUNNING.value,
        "workflow_hash": "different_hash_123",
        "tasks": {},
    }

    (run_dir / "run.json").write_text(json.dumps(run_json))

    manager = RecoveryManager(run_dir)

    with pytest.raises(RecoveryError) as exc_info:
        manager.resume_workflow()

    assert "snapshot validation failed" in str(exc_info.value).lower()
