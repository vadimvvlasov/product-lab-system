"""Run state models."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from graph_engine.models.enums import ErrorCategory, RunStatus, TaskStatus


@dataclass
class ErrorRecord:
    """Single error or failure record."""
    category: ErrorCategory
    message: str
    timestamp: str
    task_id: Optional[str] = None
    attempt: Optional[int] = None
    details: dict = field(default_factory=dict)


@dataclass
class TaskState:
    """Runtime task state."""
    task_id: str
    status: TaskStatus
    current_attempt: int = 0
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    errors: list[ErrorRecord] = field(default_factory=list)
    block_reason: Optional[str] = None


@dataclass
class RunState:
    """Complete run state snapshot."""
    schema_version: str
    run_id: str
    workflow_id: str
    status: RunStatus
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    
    # Snapshots
    workflow_snapshot_hash: str = ""
    executor_config_hash: str = ""
    git_sha: Optional[str] = None
    git_dirty: bool = False
    engine_version: str = ""
    
    # Execution
    max_concurrency: int = 1
    max_retries: int = 0
    max_run_duration_minutes: Optional[int] = None
    active_execution_seconds: int = 0
    
    # Task states
    tasks: dict[str, TaskState] = field(default_factory=dict)
    
    # Errors
    run_errors: list[ErrorRecord] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        """Convert to JSON-serializable dict."""
        return {
            "schema_version": self.schema_version,
            "run_id": self.run_id,
            "workflow_id": self.workflow_id,
            "status": self.status.value,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "workflow_snapshot_hash": self.workflow_snapshot_hash,
            "executor_config_hash": self.executor_config_hash,
            "git_sha": self.git_sha,
            "git_dirty": self.git_dirty,
            "engine_version": self.engine_version,
            "max_concurrency": self.max_concurrency,
            "max_retries": self.max_retries,
            "max_run_duration_minutes": self.max_run_duration_minutes,
            "active_execution_seconds": self.active_execution_seconds,
            "tasks": {
                task_id: {
                    "task_id": task.task_id,
                    "status": task.status.value,
                    "current_attempt": task.current_attempt,
                    "started_at": task.started_at,
                    "completed_at": task.completed_at,
                    "errors": [
                        {
                            "category": err.category.value,
                            "message": err.message,
                            "timestamp": err.timestamp,
                            "task_id": err.task_id,
                            "attempt": err.attempt,
                            "details": err.details,
                        }
                        for err in task.errors
                    ],
                    "block_reason": task.block_reason,
                }
                for task_id, task in self.tasks.items()
            },
            "run_errors": [
                {
                    "category": err.category.value,
                    "message": err.message,
                    "timestamp": err.timestamp,
                    "details": err.details,
                }
                for err in self.run_errors
            ],
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "RunState":
        """Load from dict."""
        tasks = {}
        for task_id, task_data in data.get("tasks", {}).items():
            tasks[task_id] = TaskState(
                task_id=task_data["task_id"],
                status=TaskStatus(task_data["status"]),
                current_attempt=task_data.get("current_attempt", 0),
                started_at=task_data.get("started_at"),
                completed_at=task_data.get("completed_at"),
                errors=[
                    ErrorRecord(
                        category=ErrorCategory(err["category"]),
                        message=err["message"],
                        timestamp=err["timestamp"],
                        task_id=err.get("task_id"),
                        attempt=err.get("attempt"),
                        details=err.get("details", {}),
                    )
                    for err in task_data.get("errors", [])
                ],
                block_reason=task_data.get("block_reason"),
            )
        
        return cls(
            schema_version=data["schema_version"],
            run_id=data["run_id"],
            workflow_id=data["workflow_id"],
            status=RunStatus(data["status"]),
            created_at=data["created_at"],
            started_at=data.get("started_at"),
            completed_at=data.get("completed_at"),
            workflow_snapshot_hash=data.get("workflow_snapshot_hash", ""),
            executor_config_hash=data.get("executor_config_hash", ""),
            git_sha=data.get("git_sha"),
            git_dirty=data.get("git_dirty", False),
            engine_version=data.get("engine_version", ""),
            max_concurrency=data.get("max_concurrency", 1),
            max_retries=data.get("max_retries", 0),
            max_run_duration_minutes=data.get("max_run_duration_minutes"),
            active_execution_seconds=data.get("active_execution_seconds", 0),
            tasks=tasks,
            run_errors=[
                ErrorRecord(
                    category=ErrorCategory(err["category"]),
                    message=err["message"],
                    timestamp=err["timestamp"],
                    details=err.get("details", {}),
                )
                for err in data.get("run_errors", [])
            ],
        )
