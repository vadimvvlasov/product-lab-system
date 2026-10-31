"""Base verification types and protocols."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Protocol
from pathlib import Path


class VerificationMethod(str, Enum):
    """Verification method types."""
    COMMAND = "command"
    AGENT = "agent"
    HUMAN = "human"


class VerificationStatus(str, Enum):
    """Verification result status."""
    PASS = "pass"
    FAIL = "fail"
    ERROR = "error"  # Verification itself failed to run
    PENDING = "pending"  # Human approval not yet decided


@dataclass
class VerificationCriterion:
    """Single verification criterion from workflow."""
    
    id: str
    method: VerificationMethod
    
    # Command-specific
    command: Optional[str] = None
    timeout_seconds: int = 300
    
    # Agent-specific
    executor: Optional[str] = None
    acceptance_criteria: Optional[str] = None
    
    # Human-specific
    prompt: Optional[str] = None


@dataclass
class VerificationResult:
    """Result of running a verification criterion."""
    
    criterion_id: str
    status: VerificationStatus
    message: str
    
    # Evidence
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    exit_code: Optional[int] = None
    duration_seconds: Optional[float] = None
    
    # Human decision
    approver: Optional[str] = None
    approval_comment: Optional[str] = None
    
    # Structured findings (for agent verifiers)
    findings: list[str] = field(default_factory=list)
    
    # Error details
    error_details: Optional[str] = None


class Verifier(Protocol):
    """Protocol for verification implementations."""
    
    def verify(
        self,
        criterion: VerificationCriterion,
        staging_dir: Path,
        task_context: dict,
    ) -> VerificationResult:
        """
        Run verification.
        
        Args:
            criterion: Verification criterion
            staging_dir: Working directory for verification
            task_context: Task-specific context (task_id, artifacts, etc.)
        
        Returns:
            Verification result
        """
        ...
