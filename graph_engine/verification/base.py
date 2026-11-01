"""Base verification types and protocols."""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional, Protocol

from graph_engine.models.enums import VerificationMethod
from graph_engine.models.workflow import VerificationCriterion

__all__ = [
    "VerificationCriterion",
    "VerificationMethod",
    "VerificationResult",
    "VerificationStatus",
    "Verifier",
]


class VerificationStatus(str, Enum):
    """Verification result status."""
    PASS = "pass"
    FAIL = "fail"
    ERROR = "error"  # Verification itself failed to run
    PENDING = "pending"  # Human approval not yet decided


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
