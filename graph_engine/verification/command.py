"""Command-based verification."""

import shlex
import subprocess
import time
from pathlib import Path

from graph_engine.verification.base import (
    VerificationCriterion,
    VerificationResult,
    VerificationStatus,
)


class CommandVerifier:
    """Verifies task completion using shell commands."""

    def __init__(self, max_output_bytes: int = 10_000):
        """
        Initialize command verifier.

        Args:
            max_output_bytes: Maximum bytes to capture in result (truncate larger)
        """
        self.max_output_bytes = max_output_bytes

    def verify(
        self,
        criterion: VerificationCriterion,
        staging_dir: Path,
        task_context: dict,
    ) -> VerificationResult:
        """
        Run command verification.

        Command is parsed with shlex and executed without a shell, so shell
        metacharacters are passed literally to the program. Workflow commands
        are trusted input: shell=False prevents shell interpretation, not
        arbitrary program execution, and is not a sandbox.
        """
        if not criterion.command:
            return VerificationResult(
                criterion_id=criterion.id,
                status=VerificationStatus.ERROR,
                message="Command criterion missing 'command' field",
                error_details="Configuration error",
            )

        # Parse command (no shell features allowed)
        try:
            argv = shlex.split(criterion.command)
        except ValueError as e:
            return VerificationResult(
                criterion_id=criterion.id,
                status=VerificationStatus.ERROR,
                message=f"Failed to parse command: {e}",
                error_details=str(e),
            )

        if not argv:
            return VerificationResult(
                criterion_id=criterion.id,
                status=VerificationStatus.ERROR,
                message="Command is empty after parsing",
                error_details="Empty argv",
            )

        # Run command
        start_time = time.monotonic()

        try:
            result = subprocess.run(
                argv,
                cwd=staging_dir,
                capture_output=True,
                text=True,
                timeout=criterion.timeout_seconds,
                # No shell, clean environment
                shell=False,
                env={"PATH": "/usr/bin:/bin"},  # Minimal safe PATH
            )

            duration = time.monotonic() - start_time

            # Truncate output if needed
            stdout = result.stdout
            stderr = result.stderr
            truncated = False

            if len(stdout) > self.max_output_bytes:
                stdout = (
                    stdout[: self.max_output_bytes] + "\n[truncated: output too long]"
                )
                truncated = True

            if len(stderr) > self.max_output_bytes:
                stderr = (
                    stderr[: self.max_output_bytes] + "\n[truncated: output too long]"
                )
                truncated = True

            # Exit code 0 = PASS, non-zero = FAIL
            if result.returncode == 0:
                status = VerificationStatus.PASS
                message = f"Command passed (exit {result.returncode})"
            else:
                status = VerificationStatus.FAIL
                message = f"Command failed (exit {result.returncode})"

            return VerificationResult(
                criterion_id=criterion.id,
                status=status,
                message=message,
                stdout=stdout,
                stderr=stderr,
                exit_code=result.returncode,
                duration_seconds=round(duration, 3),
            )

        except subprocess.TimeoutExpired:
            duration = time.monotonic() - start_time
            return VerificationResult(
                criterion_id=criterion.id,
                status=VerificationStatus.ERROR,
                message=f"Command timed out after {criterion.timeout_seconds}s",
                duration_seconds=round(duration, 3),
                error_details="Timeout",
            )

        except FileNotFoundError as e:
            duration = time.monotonic() - start_time
            return VerificationResult(
                criterion_id=criterion.id,
                status=VerificationStatus.ERROR,
                message=f"Command not found: {argv[0]}",
                duration_seconds=round(duration, 3),
                error_details=str(e),
            )

        except Exception as e:
            duration = time.monotonic() - start_time
            return VerificationResult(
                criterion_id=criterion.id,
                status=VerificationStatus.ERROR,
                message=f"Verification error: {type(e).__name__}: {e}",
                duration_seconds=round(duration, 3),
                error_details=str(e),
            )
