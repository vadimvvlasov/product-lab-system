"""Verification engine that runs completion criteria."""

from pathlib import Path
from typing import Optional

from graph_engine.verification.base import (
    VerificationCriterion,
    VerificationResult,
    VerificationStatus,
)
from graph_engine.verification.command import CommandVerifier
from graph_engine.verification.agent import AgentVerifier
from graph_engine.verification.human import HumanVerifier


class VerificationEngine:
    """Runs verification criteria for task completion."""
    
    def __init__(
        self,
        executor_registry,
        approval_store,
    ):
        """
        Initialize verification engine.
        
        Args:
            executor_registry: ExecutorRegistry for agent verifiers
            approval_store: ApprovalStore for human verifiers
        """
        self.command_verifier = CommandVerifier()
        self.agent_verifier = AgentVerifier(executor_registry)
        self.human_verifier = HumanVerifier(approval_store)
    
    def verify_all(
        self,
        criteria: list[VerificationCriterion],
        staging_dir: Path,
        task_context: dict,
    ) -> tuple[list[VerificationResult], bool]:
        """
        Run all verification criteria.
        
        Criteria run in declaration order.
        A failure stops remaining criteria.
        
        Args:
            criteria: List of verification criteria
            staging_dir: Working directory
            task_context: Task-specific context
        
        Returns:
            (results, all_passed) tuple
        """
        if not criteria:
            # No criteria = automatic pass
            return ([], True)
        
        results = []
        
        for criterion in criteria:
            # Run criterion
            if criterion.method.value == "command":
                result = self.command_verifier.verify(
                    criterion, staging_dir, task_context
                )
            elif criterion.method.value == "agent":
                result = self.agent_verifier.verify(
                    criterion, staging_dir, task_context
                )
            elif criterion.method.value == "human":
                result = self.human_verifier.verify(
                    criterion, staging_dir, task_context
                )
            else:
                result = VerificationResult(
                    criterion_id=criterion.id,
                    status=VerificationStatus.ERROR,
                    message=f"Unknown verification method: {criterion.method}",
                )
            
            results.append(result)
            
            # Stop on first failure or pending
            if result.status != VerificationStatus.PASS:
                break
        
        # All passed if all results are PASS
        all_passed = all(r.status == VerificationStatus.PASS for r in results)
        
        return (results, all_passed)
    
    def has_pending_approval(self, results: list[VerificationResult]) -> bool:
        """Check if any result is PENDING (awaiting human approval)."""
        return any(r.status == VerificationStatus.PENDING for r in results)
