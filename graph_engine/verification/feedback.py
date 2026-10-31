"""Build retry feedback from verification failures."""

from graph_engine.verification.base import VerificationResult, VerificationStatus
from graph_engine.execution.context import RetryFeedback


def build_retry_feedback(
    attempt_number: int,
    verification_results: list[VerificationResult],
    missing_artifacts: list[str],
) -> RetryFeedback:
    """
    Build concise retry feedback from failed attempt.
    
    Args:
        attempt_number: Failed attempt number
        verification_results: Results from all verification criteria
        missing_artifacts: List of missing/invalid artifacts
    
    Returns:
        Retry feedback for next attempt
    """
    failures = []
    reviewer_findings = []
    
    for result in verification_results:
        if result.status == VerificationStatus.FAIL:
            # Add failure message
            failures.append(f"{result.criterion_id}: {result.message}")
            
            # Include stderr from commands
            if result.stderr:
                failures.append(f"  stderr: {result.stderr[:500]}")
            
            # Include agent findings
            if result.findings:
                reviewer_findings.extend(result.findings)
        
        elif result.status == VerificationStatus.ERROR:
            # Verification itself failed
            failures.append(f"{result.criterion_id}: ERROR - {result.message}")
    
    # Combine reviewer findings into one section
    reviewer_text = None
    if reviewer_findings:
        reviewer_text = "\n".join(f"- {finding}" for finding in reviewer_findings)
    
    return RetryFeedback(
        previous_attempt=attempt_number,
        failures=failures,
        reviewer_findings=reviewer_text,
        missing_artifacts=missing_artifacts,
    )
