"""Human approval persistence."""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from graph_engine.ids import require_safe_id
from graph_engine.persistence.atomic import atomic_write_json


class ApprovalStore:
    """Stores and retrieves human approval decisions."""

    def __init__(self, run_dir: Path):
        """
        Initialize approval store.

        Args:
            run_dir: Run directory path
        """
        self.run_dir = run_dir
        self.approvals_dir = run_dir / "approvals"
        self.approvals_dir.mkdir(parents=True, exist_ok=True)

    def _approval_path(self, task_id: str) -> Path:
        """Get path to approval file for task."""
        require_safe_id(task_id, "task id")
        return self.approvals_dir / f"{task_id}.json"

    def get_approval(self, task_id: str) -> Optional[dict]:
        """
        Get approval decision for task.

        Returns:
            Decision dict or None if not yet decided:
            {
                "approved": bool,
                "approver": str,
                "comment": str or None,
                "timestamp": str (ISO 8601)
            }
        """
        path = self._approval_path(task_id)

        if not path.exists():
            return None

        try:
            with open(path, "r") as f:
                decision = json.load(f)
        except (OSError, ValueError):
            return None

        if not isinstance(decision, dict):
            return None

        return decision

    def record_approval(
        self,
        task_id: str,
        approved: bool,
        approver: Optional[str] = None,
        comment: Optional[str] = None,
    ) -> None:
        """
        Record approval decision.

        Args:
            task_id: Task identifier
            approved: True for approve, False for reject (must be a real bool)
            approver: Who approved (defaults to PLS_APPROVER or OS user)
            comment: Optional comment
        """
        if not isinstance(approved, bool):
            raise ValueError("approved must be a boolean")

        if approver is None:
            approver = os.getenv("PLS_APPROVER") or os.getenv("USER", "unknown")

        decision = {
            "approved": approved,
            "approver": approver,
            "comment": comment,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        atomic_write_json(self._approval_path(task_id), decision)

    def clear_approval(self, task_id: str) -> None:
        """Remove a previous decision (used before a new attempt)."""
        path = self._approval_path(task_id)
        try:
            path.unlink()
        except FileNotFoundError:
            pass
