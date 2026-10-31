"""Executor result models."""

from dataclasses import dataclass, field
from typing import Optional

from graph_engine.models.enums import ExecutionStatus


@dataclass
class Usage:
    """Resource usage metadata."""
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    estimated_cost: Optional[float] = None
    available: bool = True  # False if usage data not available


@dataclass
class ExecutionResult:
    """Result from executor."""
    
    status: ExecutionStatus
    summary: str
    
    # Artifacts produced
    artifacts: list[str] = field(default_factory=list)  # artifact names
    
    # Metadata
    metadata: dict = field(default_factory=dict)
    
    # Usage tracking
    usage: Optional[Usage] = None
    
    # Error details (if status = failure)
    error: Optional[str] = None
    error_details: dict = field(default_factory=dict)


def validate_result(result: ExecutionResult) -> list[str]:
    """
    Validate executor result.
    
    Returns list of validation errors (empty if valid).
    """
    errors = []
    
    # Status must be valid enum
    if not isinstance(result.status, ExecutionStatus):
        errors.append(f"Invalid status type: {type(result.status)}")
    
    # Summary required
    if not result.summary:
        errors.append("Summary is required")
    
    # Metadata must be JSON-serializable (simplified check)
    if not isinstance(result.metadata, dict):
        errors.append("Metadata must be a dict")
    
    # Usage validation
    if result.usage:
        if result.usage.input_tokens is not None and result.usage.input_tokens < 0:
            errors.append("input_tokens must be non-negative")
        if result.usage.output_tokens is not None and result.usage.output_tokens < 0:
            errors.append("output_tokens must be non-negative")
        if result.usage.estimated_cost is not None and result.usage.estimated_cost < 0:
            errors.append("estimated_cost must be non-negative")
    
    return errors
