"""Enumeration types for graph engine."""

from enum import Enum


class TaskStatus(str, Enum):
    """Task execution status."""
    PENDING = "pending"
    READY = "ready"
    RUNNING = "running"
    VERIFYING = "verifying"
    RETRYING = "retrying"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    FAILED = "failed"


class RunStatus(str, Enum):
    """Run-level status."""
    RUNNING = "running"
    AWAITING_APPROVAL = "awaiting_approval"
    COMPLETED = "completed"
    COMPLETED_WITH_BLOCKERS = "completed_with_blockers"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ExecutionStatus(str, Enum):
    """Executor result status."""
    SUCCESS = "success"
    FAILURE = "failure"
    CANCELLED = "cancelled"


class VerificationMethod(str, Enum):
    """Verification criterion method."""
    COMMAND = "command"
    AGENT = "agent"
    HUMAN = "human"


class ApprovalRequirement(str, Enum):
    """Task approval requirement."""
    NOT_REQUIRED = "not_required"
    REQUIRED = "required"


class ApprovalPoint(str, Enum):
    """When approval is checked."""
    BEFORE_EXECUTION = "before_execution"
    BEFORE_PUBLISH = "before_publish"


class SideEffects(str, Enum):
    """Task side-effect classification."""
    NONE = "none"
    IDEMPOTENT = "idempotent"
    UNSAFE = "unsafe"


class ErrorCategory(str, Enum):
    """Error classification for observability."""
    TASK_EXECUTION = "task_execution"
    VERIFICATION = "verification"
    ARTIFACT_MISSING = "artifact_missing"
    ARTIFACT_INVALID = "artifact_invalid"
    DEPENDENCY_FAILED = "dependency_failed"
    EXECUTOR_CONFIGURATION = "executor_configuration"
    APPROVAL_REJECTED = "approval_rejected"
    ORCHESTRATION = "orchestration"
    RUN_TIMEOUT = "run_timeout"
    CANCELLATION = "cancellation"
