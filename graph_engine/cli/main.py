"""Command-line interface."""

import argparse
import os
import sys

from graph_engine import __version__
from graph_engine.api import (
    approve_task,
    cancel_run,
    load_status,
    reject_task,
    resume_run,
    run_workflow,
    validate_workflow_file,
)
from graph_engine.models.enums import RunStatus

EXIT_OK = 0
EXIT_ERROR = 1
EXIT_USAGE = 2
EXIT_NOT_COMPLETED = 3
EXIT_INVALID_WORKFLOW = 4


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""
    parser = _build_parser()
    args = parser.parse_args(argv)

    if not hasattr(args, "handler"):
        parser.print_help()
        return EXIT_USAGE

    try:
        return args.handler(args)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_ERROR
    except Exception as exc:  # noqa: BLE001 - CLI reports errors, does not traceback
        print(f"error: {type(exc).__name__}: {exc}", file=sys.stderr)
        return EXIT_ERROR


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="pls", description="PLS graph engine")
    parser.add_argument("--version", action="version", version=__version__)
    sub = parser.add_subparsers(dest="command")

    validate = sub.add_parser("validate", help="validate a workflow file")
    validate.add_argument("workflow")
    validate.set_defaults(handler=_cmd_validate)

    run = sub.add_parser("run", help="create and execute a run")
    run.add_argument("workflow")
    run.add_argument("--runs-dir", default=_default_runs_dir())
    run.add_argument("--run-id")
    run.set_defaults(handler=_cmd_run)

    status = sub.add_parser("status", help="show run status")
    status.add_argument("run_dir")
    status.set_defaults(handler=_cmd_status)

    resume = sub.add_parser("resume", help="resume an interrupted or paused run")
    resume.add_argument("run_dir")
    resume.add_argument("--extend-run-timeout-minutes", type=int, default=0)
    resume.set_defaults(handler=_cmd_resume)

    approve = sub.add_parser("approve", help="approve a task")
    approve.add_argument("run_dir")
    approve.add_argument("task_id")
    approve.add_argument("--approver")
    approve.add_argument("--comment")
    approve.set_defaults(handler=_cmd_approve)

    reject = sub.add_parser("reject", help="reject a task")
    reject.add_argument("run_dir")
    reject.add_argument("task_id")
    reject.add_argument("--approver")
    reject.add_argument("--comment")
    reject.set_defaults(handler=_cmd_reject)

    cancel = sub.add_parser("cancel", help="request run cancellation")
    cancel.add_argument("run_dir")
    cancel.set_defaults(handler=_cmd_cancel)

    return parser


def _default_runs_dir() -> str:
    return os.getenv("PLS_RUNS_DIR", "runs")


def _cmd_validate(args) -> int:
    report = validate_workflow_file(args.workflow)
    print(report.format())
    return EXIT_OK if report.is_valid else EXIT_INVALID_WORKFLOW


def _cmd_run(args) -> int:
    state, layout = run_workflow(args.workflow, args.runs_dir, args.run_id)
    _print_state(state)
    print(f"run directory: {layout.run_root}")
    return _exit_for_status(state.status)


def _cmd_status(args) -> int:
    state = load_status(args.run_dir)
    _print_state(state)
    return _exit_for_status(state.status)


def _cmd_resume(args) -> int:
    state = resume_run(
        args.run_dir,
        extend_run_timeout_minutes=args.extend_run_timeout_minutes,
    )
    _print_state(state)
    return _exit_for_status(state.status)


def _cmd_approve(args) -> int:
    approve_task(args.run_dir, args.task_id, args.approver, args.comment)
    print(f"approved: {args.task_id}")
    return EXIT_OK


def _cmd_reject(args) -> int:
    reject_task(args.run_dir, args.task_id, args.approver, args.comment)
    print(f"rejected: {args.task_id}")
    return EXIT_OK


def _cmd_cancel(args) -> int:
    cancel_run(args.run_dir)
    print("cancellation requested")
    return EXIT_OK


def _print_state(state) -> None:
    print(f"run {state.run_id}: {state.status.value}")
    for task_id, task in state.tasks.items():
        line = f"  {task_id}: {task.status.value}"
        if task.block_reason:
            line += f" ({task.block_reason})"
        print(line)
    for error in state.run_errors:
        print(f"  error: {error.message}")


def _exit_for_status(status: RunStatus) -> int:
    if status == RunStatus.COMPLETED:
        return EXIT_OK
    if status in (RunStatus.AWAITING_APPROVAL, RunStatus.COMPLETED_WITH_BLOCKERS):
        return EXIT_NOT_COMPLETED
    return EXIT_ERROR


if __name__ == "__main__":
    sys.exit(main())
