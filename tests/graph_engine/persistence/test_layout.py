"""Test run layout."""

import pytest

from graph_engine.persistence.layout import RunLayout, generate_run_id, validate_run_id


def test_generate_run_id():
    """Generated run ID matches format."""
    run_id = generate_run_id("test-workflow")
    assert validate_run_id(run_id)
    assert run_id.startswith("test-workflow-")
    assert len(run_id) > 20


def test_validate_run_id():
    """Run ID validation."""
    assert validate_run_id("wf-20261031T123456Z-abc123")
    assert not validate_run_id("invalid")
    assert not validate_run_id("no-timestamp")


def test_run_layout_paths(temp_dir):
    """Layout paths are correct."""
    layout = RunLayout(temp_dir, "wf-20261031T000000Z-abc123")
    
    assert layout.run_root == temp_dir / "wf-20261031T000000Z-abc123"
    assert layout.workflow_snapshot.name == "workflow.yaml"
    assert layout.run_state.name == "run.json"
    assert layout.task_state("task-1").parts[-2:] == ("task-1", "task.json")
    assert layout.task_attempt_file("task-1", 1).name == "001.json"


def test_create_structure(temp_dir):
    """Create run directory structure."""
    layout = RunLayout(temp_dir, "wf-20261031T000000Z-abc123")
    layout.create_structure()
    
    assert layout.run_root.exists()
    assert layout.context_dir.exists()
    assert layout.tasks_dir.exists()
    assert layout.artifacts_staging_dir.exists()
    assert layout.logs_dir.exists()
