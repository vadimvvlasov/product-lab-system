"""Agent-based verification using executors."""

from pathlib import Path

from graph_engine.execution.context import ExecutionContext
from graph_engine.execution.result import ExecutionResult
from graph_engine.models.enums import ExecutionStatus
from graph_engine.verification.base import (
    VerificationCriterion,
    VerificationResult,
    VerificationStatus,
)


class AgentVerifier:
    """Verifies task completion using agent executors."""

    def __init__(self, executor_registry):
        """
        Initialize agent verifier.

        Args:
            executor_registry: ExecutorRegistry to resolve verifier executors
        """
        self.executor_registry = executor_registry

    def verify(
        self,
        criterion: VerificationCriterion,
        staging_dir: Path,
        task_context: dict,
    ) -> VerificationResult:
        """
        Run agent verification with fresh context.

        The agent verifier does NOT see the implementer's conversation.
        It receives:
        - Task definition
        - Acceptance criteria
        - Input/output artifacts
        - Evidence requirements
        """
        if not criterion.executor:
            return VerificationResult(
                criterion_id=criterion.id,
                status=VerificationStatus.ERROR,
                message="Agent criterion missing 'executor' field",
                error_details="Configuration error",
            )

        # Resolve executor through the production registry interface.
        # ExecutorRegistry exposes get_executor(); tests must use the same
        # interface so that an integration mismatch cannot hide behind a stub.
        try:
            executor = self.executor_registry.get_executor(criterion.executor)
        except KeyError:
            return VerificationResult(
                criterion_id=criterion.id,
                status=VerificationStatus.ERROR,
                message=f"Verifier executor not found: {criterion.executor}",
                error_details=f"Unknown executor: {criterion.executor}",
            )
        except Exception as e:  # noqa: BLE001 - registry errors must not crash verification
            return VerificationResult(
                criterion_id=criterion.id,
                status=VerificationStatus.ERROR,
                message=f"Cannot resolve verifier executor: {type(e).__name__}: {e}",
                error_details=str(e),
            )

        # Build fresh verification context
        # This is independent from the implementation context
        verification_context = ExecutionContext(
            task_id=task_context.get("task_id", "unknown"),
            task_type="verification",
            goal=criterion.acceptance_criteria or "Review the task completion",
            acceptance_criteria=[
                criterion.acceptance_criteria or "Verify task meets requirements",
            ],
            input_artifacts=task_context.get("input_artifacts", {}),
            required_outputs=task_context.get("required_outputs", {}),
            staging_dir=staging_dir,
            attempt_number=1,
            retry_feedback=None,
        )

        # Execute verification
        try:
            result: ExecutionResult = executor.execute(
                context=verification_context,
            )

            # Map executor result to verification result
            if result.status == ExecutionStatus.SUCCESS:
                status = VerificationStatus.PASS
                message = "Agent verification passed"
            elif result.status == ExecutionStatus.FAILURE:
                status = VerificationStatus.FAIL
                message = result.error or "Agent verification failed"
            else:
                status = VerificationStatus.ERROR
                message = f"Unexpected executor status: {result.status}"

            # Extract findings from metadata
            findings = []
            if "findings" in result.metadata:
                findings = result.metadata["findings"]
            elif result.error:
                findings = [result.error]

            return VerificationResult(
                criterion_id=criterion.id,
                status=status,
                message=message,
                findings=findings,
            )

        except Exception as e:
            return VerificationResult(
                criterion_id=criterion.id,
                status=VerificationStatus.ERROR,
                message=f"Agent verification error: {type(e).__name__}: {e}",
                error_details=str(e),
            )
