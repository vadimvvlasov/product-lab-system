"""Tests for the CLI."""

import pytest

from graph_engine.persistence.approval_store import ApprovalStore
from graph_engine.persistence.layout import RunLayout

from graph_engine.cli.main import (
    EXIT_INVALID_WORKFLOW,
    EXIT_NOT_COMPLETED,
    EXIT_OK,
    EXIT_USAGE,
    main,
)

WORKFLOW = """version: "1"
workflow:
  id: cli-test
  description: CLI test
execution:
  max_concurrency: 1
  max_retries: 0
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


def write_workflow(tmp_path, content=WORKFLOW):
    path = tmp_path / "workflow.yaml"
    path.write_text(content)
    return path


def test_validate_valid_workflow(tmp_path, capsys):
    path = write_workflow(tmp_path)

    assert main(["validate", str(path)]) == EXIT_OK
    assert "valid" in capsys.readouterr().out.lower()


def test_validate_invalid_workflow(tmp_path):
    path = write_workflow(tmp_path, WORKFLOW.replace("artifacts/a.txt", "/abs.txt"))

    assert main(["validate", str(path)]) == EXIT_INVALID_WORKFLOW


def test_run_and_status(tmp_path, capsys):
    path = write_workflow(tmp_path)
    runs_dir = tmp_path / "runs"

    assert main(["run", str(path), "--runs-dir", str(runs_dir)]) == EXIT_OK

    run_dir = next(runs_dir.iterdir())
    assert main(["status", str(run_dir)]) == EXIT_OK
    assert "completed" in capsys.readouterr().out.lower()


def test_no_command_is_usage_error(capsys):
    assert main([]) == EXIT_USAGE


def test_unknown_command_is_usage_error():
    with pytest.raises(SystemExit) as exc_info:
        main(["graph"])

    assert exc_info.value.code == EXIT_USAGE


APPROVAL_WORKFLOW = WORKFLOW.replace(
    "    type: work\n    outputs:",
    "    type: work\n    approval: required\n    approval_point: before_execution\n"
    "    outputs:",
)


def start_paused_run(tmp_path):
    path = write_workflow(tmp_path, APPROVAL_WORKFLOW)
    runs_dir = tmp_path / "runs"
    assert main(["run", str(path), "--runs-dir", str(runs_dir)]) == EXIT_NOT_COMPLETED
    return next(runs_dir.iterdir())


def test_approve_and_resume(tmp_path, capsys):
    run_dir = start_paused_run(tmp_path)
    assert "awaiting_approval" in main_status(run_dir, capsys, EXIT_NOT_COMPLETED)

    assert main(["approve", str(run_dir), "task-a", "--approver", "qa"]) == EXIT_OK

    decision = ApprovalStore(run_dir).get_approval("task-a")
    assert decision["approved"] is True
    assert (run_dir / "approvals" / "task-a.json").exists()

    assert main(["resume", str(run_dir)]) == EXIT_OK
    assert "completed" in main_status(run_dir, capsys)
    assert (run_dir / "artifacts" / "a.txt").exists()


def test_reject_blocks_task_on_resume(tmp_path, capsys):
    run_dir = start_paused_run(tmp_path)

    assert main(["reject", str(run_dir), "task-a", "--comment", "no"]) == EXIT_OK

    decision = ApprovalStore(run_dir).get_approval("task-a")
    assert decision["approved"] is False

    assert main(["resume", str(run_dir)]) == EXIT_NOT_COMPLETED
    status = main_status(run_dir, capsys, EXIT_NOT_COMPLETED)
    assert "completed_with_blockers" in status
    assert "task-a: blocked" in status
    assert not (run_dir / "artifacts" / "a.txt").exists()


def test_cancel_creates_sentinel_and_resume_clears_it(tmp_path, capsys):
    run_dir = start_paused_run(tmp_path)
    sentinel = RunLayout(run_dir.parent, run_dir.name).cancel_sentinel

    assert main(["cancel", str(run_dir)]) == EXIT_OK
    assert sentinel.exists()

    main(["approve", str(run_dir), "task-a"])
    assert main(["resume", str(run_dir)]) == EXIT_OK
    assert not sentinel.exists()
    assert "completed" in main_status(run_dir, capsys)


def main_status(run_dir, capsys, expected=EXIT_OK):
    capsys.readouterr()
    assert main(["status", str(run_dir)]) == expected
    return capsys.readouterr().out.lower()
