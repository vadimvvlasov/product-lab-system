"""End-to-end tests for the run controller."""

import pytest

from graph_engine.execution.controller import RunController
from graph_engine.execution.result import ExecutionResult
from graph_engine.models.enums import ExecutionStatus, RunStatus, TaskStatus
from graph_engine.parser import parse_workflow
from graph_engine.persistence.approval_store import ApprovalStore
from graph_engine.persistence.run_store import create_run

WORKFLOW = """version: "1"
workflow:
  id: controller-test
  description: Controller test
execution:
  max_concurrency: 1
  max_retries: 1
  max_run_duration_minutes: 5
executors:
  worker:
    adapter: mock
    config: {}
executor_mapping:
  work: worker
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
  - id: task-b
    type: work
    depends_on: [task-a]
    inputs:
      - name: data
        from: task-a
        artifact: out
    outputs:
      - name: out
        path: artifacts/b.txt
    verification:
      - id: check
        method: command
        command: "test -f artifacts/b.txt"
"""


class ScriptedExecutor:
    """Executor with scripted results and artifact creation."""

    name = "worker"
    adapter = "test"

    def __init__(self, results, write_artifacts=True):
        self.results = list(results)
        self.write_artifacts = write_artifacts
        self.calls = []

    def execute(self, context):
        self.calls.append(context)
        index = min(len(self.calls) - 1, len(self.results) - 1)
        result = self.results[index]

        if result.status == ExecutionStatus.SUCCESS and self.write_artifacts:
            for path in context.required_outputs.values():
                target = context.staging_dir / path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text("x" * 32)

        return result

    def cancel(self):
        pass


class DictRegistry:
    def __init__(self, executors):
        self.executors = executors

    def get_executor(self, name):
        if name not in self.executors:
            raise KeyError(name)
        return self.executors[name]


def success(summary="ok"):
    return ExecutionResult(status=ExecutionStatus.SUCCESS, summary=summary)


def failure(error="boom"):
    return ExecutionResult(status=ExecutionStatus.FAILURE, summary="failed", error=error)


def make_run(tmp_path, yaml_text=WORKFLOW, run_id="controller-test-20261031T210000Z-abcdef"):
    workflow = parse_workflow(yaml_text.encode())
    state, layout = create_run(
        workflow, yaml_text.encode(), tmp_path / "runs", run_id=run_id
    )
    return workflow, state, layout


def test_controller_runs_workflow_end_to_end(tmp_path):
    workflow, state, layout = make_run(tmp_path)
    executor = ScriptedExecutor([success(), success()])
    controller = RunController(
        workflow, layout, state, DictRegistry({"worker": executor})
    )

    result = controller.run()

    assert result.status == RunStatus.COMPLETED
    assert all(t.status == TaskStatus.COMPLETED for t in result.tasks.values())
    assert (layout.run_root / "artifacts" / "a.txt").exists()
    assert (layout.run_root / "artifacts" / "b.txt").exists()
    assert len(executor.calls) == 2
    assert result.tasks["task-a"].artifacts[0]["sha256"]

    # task-b received task-a's published artifact as declared input
    second = executor.calls[1]
    assert "data" in second.input_artifacts
    assert second.input_artifacts["data"].exists()


def test_controller_retries_with_feedback(tmp_path):
    workflow, state, layout = make_run(tmp_path)
    executor = ScriptedExecutor([failure(), success(), success()])
    controller = RunController(
        workflow, layout, state, DictRegistry({"worker": executor})
    )

    result = controller.run()

    assert result.status == RunStatus.COMPLETED
    assert result.tasks["task-a"].current_attempt == 2
    assert (layout.run_root / "tasks" / "task-a" / "attempts" / "001.json").exists()
    assert (layout.run_root / "tasks" / "task-a" / "attempts" / "002.json").exists()


def test_controller_blocks_after_verification_failure(tmp_path):
    workflow_yaml = WORKFLOW.replace(
        "test -f artifacts/a.txt", "test -f artifacts/missing.txt"
    )
    workflow, state, layout = make_run(tmp_path, workflow_yaml)
    executor = ScriptedExecutor([success(), success()])
    controller = RunController(
        workflow, layout, state, DictRegistry({"worker": executor})
    )

    result = controller.run()

    assert result.tasks["task-a"].status == TaskStatus.BLOCKED
    assert result.tasks["task-b"].status == TaskStatus.BLOCKED
    assert result.status == RunStatus.COMPLETED_WITH_BLOCKERS


def test_controller_pauses_for_approval_before_execution(tmp_path):
    workflow_yaml = WORKFLOW.replace(
        "    type: work\n    outputs:\n      - name: out\n        path: artifacts/a.txt",
        "    type: work\n    approval: required\n    approval_point: before_execution\n"
        "    outputs:\n      - name: out\n        path: artifacts/a.txt",
    )
    workflow, state, layout = make_run(tmp_path, workflow_yaml)
    executor = ScriptedExecutor([success(), success()])

    controller = RunController(
        workflow, layout, state, DictRegistry({"worker": executor})
    )
    paused = controller.run()

    assert paused.status == RunStatus.AWAITING_APPROVAL
    assert executor.calls == []

    ApprovalStore(layout.run_root).record_approval("task-a", True)
    resumed = RunController(
        workflow, layout, paused, DictRegistry({"worker": executor})
    ).run()

    assert resumed.status == RunStatus.COMPLETED
    assert len(executor.calls) == 2


def test_controller_pauses_before_publish_without_reexecuting(tmp_path):
    workflow_yaml = WORKFLOW.replace(
        "    type: work\n    outputs:\n      - name: out\n        path: artifacts/a.txt",
        "    type: work\n    approval: required\n"
        "    outputs:\n      - name: out\n        path: artifacts/a.txt",
    )
    workflow, state, layout = make_run(tmp_path, workflow_yaml)
    executor = ScriptedExecutor([success(), success()])

    controller = RunController(
        workflow, layout, state, DictRegistry({"worker": executor})
    )
    paused = controller.run()

    assert paused.status == RunStatus.AWAITING_APPROVAL
    assert paused.tasks["task-a"].status == TaskStatus.VERIFYING
    assert len(executor.calls) == 1
    assert not (layout.run_root / "artifacts" / "a.txt").exists()

    ApprovalStore(layout.run_root).record_approval("task-a", True)
    resumed = RunController(
        workflow, layout, paused, DictRegistry({"worker": executor})
    ).run()

    assert resumed.status == RunStatus.COMPLETED
    assert len(executor.calls) == 2  # one call for a, one for b; no re-execution
    assert (layout.run_root / "artifacts" / "a.txt").exists()


def test_controller_stops_on_cancel_sentinel(tmp_path):
    workflow, state, layout = make_run(tmp_path)
    layout.cancel_sentinel.write_text("cancel")
    executor = ScriptedExecutor([success(), success()])

    result = RunController(
        workflow, layout, state, DictRegistry({"worker": executor})
    ).run()

    assert result.status == RunStatus.CANCELLED
    assert executor.calls == []


def test_controller_fails_on_run_timeout(tmp_path):
    workflow, state, layout = make_run(tmp_path)
    state.active_execution_seconds = 60 * 5
    executor = ScriptedExecutor([success(), success()])

    result = RunController(
        workflow, layout, state, DictRegistry({"worker": executor})
    ).run()

    assert result.status == RunStatus.FAILED
    assert executor.calls == []


class ContentExecutor(ScriptedExecutor):
    """Writes per-call content so verification can pass or fail by attempt."""

    def __init__(self, contents):
        super().__init__([success()])
        self.contents = contents

    def execute(self, context):
        self.calls.append(context)
        content = self.contents[min(len(self.calls) - 1, len(self.contents) - 1)]
        for path in context.required_outputs.values():
            target = context.staging_dir / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content)
        return success()


def _attempt(layout, task_id, number):
    import json

    path = layout.run_root / "tasks" / task_id / "attempts" / f"{number:03d}.json"
    return json.loads(path.read_text())


def test_controller_retries_after_verification_failure(tmp_path):
    workflow_yaml = WORKFLOW.replace(
        "test -f artifacts/a.txt", "grep -q ok artifacts/a.txt"
    )
    workflow, state, layout = make_run(tmp_path, workflow_yaml)
    executor = ContentExecutor(["bad content", "ok content"])

    result = RunController(
        workflow, layout, state, DictRegistry({"worker": executor})
    ).run()

    assert result.status == RunStatus.COMPLETED
    # task-a twice (verification failed once), task-b once
    assert [c.task_id for c in executor.calls] == ["task-a", "task-a", "task-b"]
    second = executor.calls[1]
    assert second.attempt_number == 2
    assert second.retry_feedback is not None
    assert second.retry_feedback.failures
    assert any("check" in f for f in second.retry_feedback.failures)
    assert _attempt(layout, "task-a", 1)["status"] == "failed"


def test_verification_failure_with_artifacts_present_has_no_missing(tmp_path, monkeypatch):
    from graph_engine.execution import controller as controller_module

    seen = []
    real = controller_module.build_retry_feedback

    def spy(attempt, results, missing):
        seen.append(list(missing))
        return real(attempt, results, missing)

    monkeypatch.setattr(controller_module, "build_retry_feedback", spy)
    workflow_yaml = WORKFLOW.replace(
        "test -f artifacts/a.txt", "grep -q ok artifacts/a.txt"
    )
    workflow, state, layout = make_run(tmp_path, workflow_yaml)
    executor = ContentExecutor(["bad content", "ok content"])

    RunController(workflow, layout, state, DictRegistry({"worker": executor})).run()

    assert seen == [[]]
    assert _attempt(layout, "task-a", 1)["retry_feedback"]["missing_artifacts"] == []
    assert executor.calls[1].retry_feedback.missing_artifacts == []


def test_verification_removing_output_lists_only_that_output(tmp_path):
    workflow_yaml = WORKFLOW.replace(
        'command: "test -f artifacts/a.txt"',
        "command: \"sh -c 'rm artifacts/a.txt; false'\"",
    )
    workflow, state, layout = make_run(tmp_path, workflow_yaml)
    executor = ScriptedExecutor([success()])

    RunController(workflow, layout, state, DictRegistry({"worker": executor})).run()

    assert _attempt(layout, "task-a", 1)["retry_feedback"]["missing_artifacts"] == ["out"]
    assert executor.calls[1].retry_feedback.missing_artifacts == ["out"]


class _FakeTime:
    def __init__(self, values):
        self.values = iter(values)

    def monotonic(self):
        return next(self.values)


def test_subsecond_tasks_accumulate_active_execution_seconds(tmp_path, monkeypatch):
    from graph_engine.execution import controller as controller_module

    workflow, state, layout = make_run(tmp_path)
    monkeypatch.setattr(
        controller_module, "time", _FakeTime([0.0, 0.4, 0.4, 0.8])
    )
    executor = ScriptedExecutor([success(), success()])

    result = RunController(
        workflow, layout, state, DictRegistry({"worker": executor})
    ).run()

    assert result.status == RunStatus.COMPLETED
    assert result.active_execution_seconds == pytest.approx(0.8)

    from graph_engine.persistence import load_run_state

    loaded = load_run_state(layout)
    assert isinstance(loaded.active_execution_seconds, float)
    assert loaded.active_execution_seconds == pytest.approx(0.8)


def test_crashed_executor_accumulates_elapsed_time(tmp_path, monkeypatch):
    from graph_engine.execution import controller as controller_module

    class Crashing(ScriptedExecutor):
        def execute(self, context):
            raise RuntimeError("boom")

    workflow, state, layout = make_run(tmp_path)
    monkeypatch.setattr(
        controller_module, "time", _FakeTime([10.0, 10.25, 10.25, 10.5])
    )
    RunController(
        workflow, layout, state, DictRegistry({"worker": Crashing([success()])})
    ).run()

    assert state.active_execution_seconds == pytest.approx(0.5)


def test_run_state_loads_integer_active_execution_seconds(tmp_path):
    from graph_engine.models.run import RunState

    workflow, state, layout = make_run(tmp_path)
    data = state.to_dict()
    data["active_execution_seconds"] = 7

    loaded = RunState.from_dict(data)

    assert loaded.active_execution_seconds == 7.0
    assert isinstance(loaded.active_execution_seconds, float)
