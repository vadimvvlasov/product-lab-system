"""Tests for task status reconciliation."""

import pytest
from pathlib import Path

from graph_engine.recovery.reconcile import reconcile_task_status
from graph_engine.models.enums import TaskStatus


@pytest.fixture
def temp_artifacts(tmp_path):
    """Create temporary artifacts directory."""
    artifacts = tmp_path / "artifacts"
    artifacts.mkdir()
    return artifacts


def test_reconcile_completed_with_valid_artifacts(temp_artifacts):
    """Test completed task with valid artifacts is reused."""
    # Create artifact
    (temp_artifacts / "report.md").write_text("Report content")
    
    recon = reconcile_task_status(
        task_id="task1",
        current_status=TaskStatus.COMPLETED,
        artifacts_dir=temp_artifacts,
        required_artifacts=[{"name": "report", "path": "report.md"}],
        side_effects="none",
    )
    
    assert recon.old_status == TaskStatus.COMPLETED
    assert recon.new_status == TaskStatus.COMPLETED
    assert recon.safe is True
    assert recon.artifacts_valid is True
    assert recon.reuse is True
    assert "reusing" in recon.reason.lower()


def test_reconcile_completed_with_missing_artifacts_safe(temp_artifacts):
    """Test completed task with missing artifacts is reset to pending."""
    # No artifacts created
    
    recon = reconcile_task_status(
        task_id="task1",
        current_status=TaskStatus.COMPLETED,
        artifacts_dir=temp_artifacts,
        required_artifacts=[{"name": "report", "path": "report.md"}],
        side_effects="none",
    )
    
    assert recon.old_status == TaskStatus.COMPLETED
    assert recon.new_status == TaskStatus.PENDING
    assert recon.safe is True
    assert recon.artifacts_valid is False
    assert recon.missing_artifacts == ["report"]
    assert "re-execute" in recon.reason.lower()


def test_reconcile_completed_with_missing_artifacts_unsafe(temp_artifacts):
    """Test completed task with missing artifacts and unsafe side effects is blocked."""
    # No artifacts created
    
    recon = reconcile_task_status(
        task_id="task1",
        current_status=TaskStatus.COMPLETED,
        artifacts_dir=temp_artifacts,
        required_artifacts=[{"name": "report", "path": "report.md"}],
        side_effects="unsafe",
    )
    
    assert recon.old_status == TaskStatus.COMPLETED
    assert recon.new_status == TaskStatus.BLOCKED
    assert recon.safe is False
    assert recon.artifacts_valid is False
    assert recon.missing_artifacts == ["report"]
    assert "unsafe" in recon.reason.lower()


def test_reconcile_running_safe(temp_artifacts):
    """Test interrupted running task is reset to pending."""
    recon = reconcile_task_status(
        task_id="task1",
        current_status=TaskStatus.RUNNING,
        artifacts_dir=temp_artifacts,
        required_artifacts=[],
        side_effects="none",
    )
    
    assert recon.old_status == TaskStatus.RUNNING
    assert recon.new_status == TaskStatus.PENDING
    assert recon.safe is True
    assert "restart" in recon.reason.lower()


def test_reconcile_running_unsafe(temp_artifacts):
    """Test interrupted running task with unsafe side effects is blocked."""
    recon = reconcile_task_status(
        task_id="task1",
        current_status=TaskStatus.RUNNING,
        artifacts_dir=temp_artifacts,
        required_artifacts=[],
        side_effects="unsafe",
    )
    
    assert recon.old_status == TaskStatus.RUNNING
    assert recon.new_status == TaskStatus.BLOCKED
    assert recon.safe is False
    assert "unsafe" in recon.reason.lower()


def test_reconcile_verifying_safe(temp_artifacts):
    """Test interrupted verifying task is reset to pending."""
    recon = reconcile_task_status(
        task_id="task1",
        current_status=TaskStatus.VERIFYING,
        artifacts_dir=temp_artifacts,
        required_artifacts=[],
        side_effects="idempotent",
    )
    
    assert recon.old_status == TaskStatus.VERIFYING
    assert recon.new_status == TaskStatus.PENDING
    assert recon.safe is True


def test_reconcile_blocked_preserved(temp_artifacts):
    """Test blocked status is preserved."""
    recon = reconcile_task_status(
        task_id="task1",
        current_status=TaskStatus.BLOCKED,
        artifacts_dir=temp_artifacts,
        required_artifacts=[],
        side_effects="none",
    )
    
    assert recon.old_status == TaskStatus.BLOCKED
    assert recon.new_status == TaskStatus.BLOCKED
    assert recon.safe is True
    assert "preserved" in recon.reason.lower()


def test_reconcile_failed_preserved(temp_artifacts):
    """Test failed status is preserved."""
    recon = reconcile_task_status(
        task_id="task1",
        current_status=TaskStatus.FAILED,
        artifacts_dir=temp_artifacts,
        required_artifacts=[],
        side_effects="none",
    )
    
    assert recon.old_status == TaskStatus.FAILED
    assert recon.new_status == TaskStatus.FAILED
    assert recon.safe is True


def test_reconcile_ready_to_pending(temp_artifacts):
    """Test ready task returns to pending."""
    recon = reconcile_task_status(
        task_id="task1",
        current_status=TaskStatus.READY,
        artifacts_dir=temp_artifacts,
        required_artifacts=[],
        side_effects="none",
    )
    
    assert recon.old_status == TaskStatus.READY
    assert recon.new_status == TaskStatus.PENDING
    assert recon.safe is True


def test_reconcile_retrying_to_pending(temp_artifacts):
    """Test retrying task returns to pending."""
    recon = reconcile_task_status(
        task_id="task1",
        current_status=TaskStatus.RETRYING,
        artifacts_dir=temp_artifacts,
        required_artifacts=[],
        side_effects="none",
    )
    
    assert recon.old_status == TaskStatus.RETRYING
    assert recon.new_status == TaskStatus.PENDING
    assert recon.safe is True


def test_reconcile_pending_preserved(temp_artifacts):
    """Test pending status is preserved."""
    recon = reconcile_task_status(
        task_id="task1",
        current_status=TaskStatus.PENDING,
        artifacts_dir=temp_artifacts,
        required_artifacts=[],
        side_effects="none",
    )
    
    assert recon.old_status == TaskStatus.PENDING
    assert recon.new_status == TaskStatus.PENDING
    assert recon.safe is True


def test_reconcile_multiple_missing_artifacts(temp_artifacts):
    """Test multiple missing artifacts are reported."""
    # Create only one of two artifacts
    (temp_artifacts / "report.md").write_text("Report")
    
    recon = reconcile_task_status(
        task_id="task1",
        current_status=TaskStatus.COMPLETED,
        artifacts_dir=temp_artifacts,
        required_artifacts=[
            {"name": "report", "path": "report.md"},
            {"name": "metrics", "path": "metrics.json"},
        ],
        side_effects="none",
    )
    
    assert recon.artifacts_valid is False
    assert recon.missing_artifacts == ["metrics"]
    assert recon.new_status == TaskStatus.PENDING
