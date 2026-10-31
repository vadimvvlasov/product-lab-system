"""Persistence and state management."""

from graph_engine.persistence.atomic import (
    atomic_append_jsonl,
    atomic_read_json,
    atomic_write_json,
)
from graph_engine.persistence.layout import RunLayout, generate_run_id, validate_run_id
from graph_engine.persistence.run_store import create_run, load_run_state, save_run_state
from graph_engine.persistence.snapshot import (
    compute_hash,
    snapshot_executor_config,
    snapshot_workflow,
    verify_snapshot_hash,
)

__all__ = [
    # Atomic I/O
    "atomic_write_json",
    "atomic_read_json",
    "atomic_append_jsonl",
    # Layout
    "RunLayout",
    "generate_run_id",
    "validate_run_id",
    # Run store
    "create_run",
    "save_run_state",
    "load_run_state",
    # Snapshots
    "snapshot_workflow",
    "snapshot_executor_config",
    "compute_hash",
    "verify_snapshot_hash",
]
