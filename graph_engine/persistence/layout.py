"""Run directory layout and ID generation."""

import hashlib
import re
from datetime import datetime, timezone
from pathlib import Path


def generate_run_id(workflow_id: str) -> str:
    """
    Generate a unique run ID.
    
    Format: <workflow-id>-YYYYMMDDTHHMMSSZ-<6-hex>
    
    Args:
        workflow_id: Workflow identifier
        
    Returns:
        Run ID string
    """
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    
    # Add entropy from timestamp + random component
    entropy = hashlib.sha256(
        f"{workflow_id}{timestamp}{datetime.now().timestamp()}".encode()
    ).hexdigest()[:6]
    
    return f"{workflow_id}-{timestamp}-{entropy}"


def validate_run_id(run_id: str) -> bool:
    """Check if run ID matches expected format."""
    # Pattern: alphanumeric-dash_TIMESTAMP_hex
    pattern = r'^[a-zA-Z0-9_-]+-\d{8}T\d{6}Z-[0-9a-f]{6}$'
    return bool(re.match(pattern, run_id))


class RunLayout:
    """
    Run directory structure manager.
    
    Layout:
    runs/<run-id>/
      workflow.yaml              # immutable snapshot
      executor_config.json       # normalized config snapshot
      run.json                   # authoritative state
      run.lock                   # advisory lock
      context/                   # snapshotted instructions
      tasks/<task-id>/task.json
      tasks/<task-id>/attempts/001.json
      approvals/<task-id>.json
      artifacts/.staging/<task-id>/attempt-001/
      artifacts/<...>            # published outputs
      logs/events.jsonl
      metrics.json
    """
    
    def __init__(self, runs_dir: Path, run_id: str):
        """
        Initialize run layout.
        
        Args:
            runs_dir: Base runs directory
            run_id: Run identifier
        """
        if not validate_run_id(run_id):
            raise ValueError(f"Invalid run ID format: {run_id}")
        
        self.runs_dir = runs_dir
        self.run_id = run_id
        self.run_root = runs_dir / run_id
    
    # Top-level files
    @property
    def workflow_snapshot(self) -> Path:
        """Immutable workflow YAML snapshot."""
        return self.run_root / "workflow.yaml"
    
    @property
    def executor_config_snapshot(self) -> Path:
        """Executor configuration snapshot."""
        return self.run_root / "executor_config.json"
    
    @property
    def run_state(self) -> Path:
        """Authoritative run state JSON."""
        return self.run_root / "run.json"
    
    @property
    def run_lock(self) -> Path:
        """Advisory lock file."""
        return self.run_root / "run.lock"
    
    @property
    def cancel_sentinel(self) -> Path:
        """Cancellation request sentinel."""
        return self.run_root / "cancel.requested"
    
    # Directories
    @property
    def context_dir(self) -> Path:
        """Snapshotted context files."""
        return self.run_root / "context"
    
    @property
    def tasks_dir(self) -> Path:
        """Task state projections."""
        return self.run_root / "tasks"
    
    @property
    def approvals_dir(self) -> Path:
        """Approval decisions."""
        return self.run_root / "approvals"
    
    @property
    def artifacts_dir(self) -> Path:
        """Published artifacts."""
        return self.run_root / "artifacts"
    
    @property
    def artifacts_staging_dir(self) -> Path:
        """Staging area for unpublished outputs."""
        return self.artifacts_dir / ".staging"
    
    @property
    def logs_dir(self) -> Path:
        """Event logs."""
        return self.run_root / "logs"
    
    @property
    def events_log(self) -> Path:
        """JSONL events."""
        return self.logs_dir / "events.jsonl"
    
    @property
    def metrics_file(self) -> Path:
        """Aggregated metrics."""
        return self.run_root / "metrics.json"
    
    # Task-specific
    def task_state(self, task_id: str) -> Path:
        """Task state projection."""
        return self.tasks_dir / task_id / "task.json"
    
    def task_attempts_dir(self, task_id: str) -> Path:
        """Task attempts directory."""
        return self.tasks_dir / task_id / "attempts"
    
    def task_attempt_file(self, task_id: str, attempt: int) -> Path:
        """Attempt record JSON."""
        return self.task_attempts_dir(task_id) / f"{attempt:03d}.json"
    
    def task_staging_dir(self, task_id: str, attempt: int) -> Path:
        """Attempt staging directory (executor working dir)."""
        return self.artifacts_staging_dir / task_id / f"attempt-{attempt:03d}"
    
    def task_approval(self, task_id: str) -> Path:
        """Approval decision record."""
        return self.approvals_dir / f"{task_id}.json"
    
    def create_structure(self):
        """Create initial run directory structure."""
        self.run_root.mkdir(parents=True, exist_ok=True)
        self.context_dir.mkdir(exist_ok=True)
        self.tasks_dir.mkdir(exist_ok=True)
        self.approvals_dir.mkdir(exist_ok=True)
        self.artifacts_dir.mkdir(exist_ok=True)
        self.artifacts_staging_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)
