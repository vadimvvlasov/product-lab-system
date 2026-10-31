"""Human approval verification."""

from pathlib import Path
from typing import Optional

from graph_engine.verification.base import (
    VerificationCriterion,
    VerificationResult,
    VerificationStatus,
)


class HumanVerifier:
    """Verifies task completion through human approval."""
    
    def __init__(self, approval_store):
        """
        Initialize human verifier.
        
        Args:
            approval_store: ApprovalStore for reading approval decisions
        """
        self.approval_store = approval_store
    
    def verify(
        self,
        criterion: VerificationCriterion,
        staging_dir: Path,
        task_context: dict,
    ) -> VerificationResult:
        """
        Check if human approval exists.
        
        This does NOT block. It returns PENDING if no decision exists.
        The controller must pause and wait for approval.
        """
        task_id = task_context.get("task_id", "unknown")
        
        # Check if approval exists
        decision = self.approval_store.get_approval(task_id)
        
        if decision is None:
            # No decision yet - must pause
            prompt_text = criterion.prompt or "Approve task completion"
            return VerificationResult(
                criterion_id=criterion.id,
                status=VerificationStatus.PENDING,
                message=f"Awaiting approval: {prompt_text}",
            )
        
        # Decision exists
        if decision["approved"]:
            return VerificationResult(
                criterion_id=criterion.id,
                status=VerificationStatus.PASS,
                message="Approved by human",
                approver=decision.get("approver"),
                approval_comment=decision.get("comment"),
            )
        else:
            return VerificationResult(
                criterion_id=criterion.id,
                status=VerificationStatus.FAIL,
                message="Rejected by human",
                approver=decision.get("approver"),
                approval_comment=decision.get("comment"),
            )
