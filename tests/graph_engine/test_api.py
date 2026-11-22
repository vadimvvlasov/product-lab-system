"""Tests for the public API."""

import pytest

from graph_engine.api import (
    approve_task,
    cancel_run,
    load_status,
    resume_run,
    run_workflow,
)
from graph_engine.errors import ValidationError
from graph_engine.models.enums import RunStatus, TaskStatus

WORKFLOW = """version: "1"
workflow:
  id: api-test
  description: API test
execution:
  max_concurrency: 1
  max_retries: 1
executors:
  mock:
    adapter: mock
    config:
      artifacts: [out]
executor_mapping:
  work: mock
tasks:
  - id: task-a
    type: work
    outputs:
      - name: out
        path: artifacts/a.txt
    verification:
      - id: check
        method: command
        command: "test -f artifacts/a.txt"
"""

APPROVAL_WORKFLOW = WORKFLOW.replace(
    "    type: work\n    outputs:",
    "    type: work\n    approval: required\n    outputs:",
)


def write_workflow(tmp_path, content=WORKFLOW):
    path = tmp_path / "workflow.yaml"
    path.write_text(content)
    return path


def test_run_workflow_end_to_end(tmp_path):
    workflow_path = write_workflow(tmp_path)

    state, layout = run_workflow(workflow_path, tmp_path / "runs")

    assert state.status == RunStatus.COMPLETED
    assert state.tasks["task-a"].status == TaskStatus.COMPLETED
    assert (layout.run_root / "artifacts" / "a.txt").exists()


def test_run_workflow_rejects_invalid_workflow(tmp_path):
    workflow_path = write_workflow(
        tmp_path,
        WORKFLOW.replace("artifacts/a.txt", "/absolute/path.txt"),
    )

    with pytest.raises(ValidationError):
        run_workflow(workflow_path, tmp_path / "runs")


def test_approval_pause_and_resume(tmp_path):
    workflow_path = write_workflow(tmp_path, APPROVAL_WORKFLOW)

    paused, layout = run_workflow(workflow_path, tmp_path / "runs")
    assert paused.status == RunStatus.AWAITING_APPROVAL

    approve_task(layout.run_root, "task-a", approver="owner")
    resumed = resume_run(layout.run_root)

    assert resumed.status == RunStatus.COMPLETED


def test_load_status_and_cancel(tmp_path):
    workflow_path = write_workflow(tmp_path)
    state, layout = run_workflow(workflow_path, tmp_path / "runs")

    assert load_status(layout.run_root).run_id == state.run_id

    cancel_run(layout.run_root)
    assert layout.cancel_sentinel.exists()
