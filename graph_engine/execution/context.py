"""Execution context for tasks."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class RetryFeedback:
    """Feedback from previous failed attempt."""
    previous_attempt: int
    failures: list[str]
    reviewer_findings: Optional[str] = None
    missing_artifacts: list[str] = field(default_factory=list)


@dataclass
class ExecutionContext:
    """Context passed to executor for task execution."""
    
    # Task definition
    task_id: str
    task_type: str
    goal: str  # From task definition or acceptance criteria
    acceptance_criteria: list[str]
    
    # Inputs
    input_artifacts: dict[str, Path]  # name -> path in staging
    
    # Outputs
    required_outputs: dict[str, str]  # name -> relative path
    
    # Working directory
    staging_dir: Path
    
    # Retry context
    attempt_number: int = 1
    retry_feedback: Optional[RetryFeedback] = None
    
    # Side effects
    idempotency_key: Optional[str] = None
    
    # References (snapshotted context files)
    instructions: list[Path] = field(default_factory=list)
    references: list[Path] = field(default_factory=list)
