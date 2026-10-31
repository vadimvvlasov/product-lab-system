"""Workflow definition data models."""

from dataclasses import dataclass, field
from typing import Optional

from graph_engine.models.enums import (
    ApprovalPoint,
    ApprovalRequirement,
    SideEffects,
    VerificationMethod,
)


@dataclass(frozen=True)
class WorkflowMetadata:
    """Workflow identification."""
    id: str
    description: str


@dataclass(frozen=True)
class ExecutionLimits:
    """Execution constraints."""
    max_concurrency: int
    max_retries: int
    max_run_duration_minutes: Optional[int] = None


@dataclass(frozen=True)
class ExecutorConfig:
    """Executor adapter configuration."""
    adapter: str
    config: dict[str, any] = field(default_factory=dict)


@dataclass(frozen=True)
class TaskInput:
    """Declared task input artifact."""
    name: str
    from_task: str  # source task ID (must be in depends_on)
    artifact: str   # artifact name from source task's outputs


@dataclass(frozen=True)
class TaskOutput:
    """Declared task output artifact."""
    name: str
    path: str  # relative to run root, must start with artifacts/
    min_bytes: int = 1


@dataclass(frozen=True)
class VerificationCriterion:
    """Single verification criterion."""
    id: str
    method: VerificationMethod
    # For command method
    command: Optional[str] = None
    timeout_seconds: int = 300
    # For agent method
    executor: Optional[str] = None
    acceptance_criteria: Optional[str] = None
    # For human method
    prompt: Optional[str] = None


@dataclass(frozen=True)
class ContextReference:
    """Workflow-level context references."""
    instructions: list[str] = field(default_factory=list)
    references: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class TaskDefinition:
    """Complete task definition from workflow."""
    id: str
    type: str
    executor: Optional[str] = None  # explicit executor name
    depends_on: list[str] = field(default_factory=list)
    inputs: list[TaskInput] = field(default_factory=list)
    outputs: list[TaskOutput] = field(default_factory=list)
    verification: list[VerificationCriterion] = field(default_factory=list)
    approval: ApprovalRequirement = ApprovalRequirement.NOT_REQUIRED
    approval_point: ApprovalPoint = ApprovalPoint.BEFORE_PUBLISH
    max_retries: Optional[int] = None  # overrides execution.max_retries
    timeout_minutes: Optional[int] = None
    side_effects: SideEffects = SideEffects.NONE
    idempotency_key: Optional[str] = None


@dataclass(frozen=True)
class WorkflowDefinition:
    """Complete validated workflow definition."""
    version: str
    workflow: WorkflowMetadata
    execution: ExecutionLimits
    executors: dict[str, ExecutorConfig]
    executor_mapping: dict[str, str]  # task_type -> executor_name
    tasks: list[TaskDefinition]
    context: Optional[ContextReference] = None
    
    def get_task(self, task_id: str) -> Optional[TaskDefinition]:
        """Get task by ID."""
        return next((t for t in self.tasks if t.id == task_id), None)
