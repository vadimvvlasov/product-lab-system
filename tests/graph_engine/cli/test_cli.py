"""Tests for the CLI."""

import pytest

from graph_engine.cli.main import (
    EXIT_INVALID_WORKFLOW,
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
