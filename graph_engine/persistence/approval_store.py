"""Human approval persistence."""

import os
import json
from pathlib import Path
from typing import Optional
from datetime import datetime, timezone

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
                return json.load(f)
        except (IOError, json.JSONDecodeError):
            return None
    
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
            approved: True for approve, False for reject
            approver: Who approved (defaults to OS user or PLS_APPROVER env)
            comment: Optional comment
        """
        if approver is None:
            # Try environment variable, fallback to OS user
            approver = os.getenv("PLS_APPROVER") or os.getenv("USER", "unknown")
        
        decision = {
            "approved": approved,
            "approver": approver,
            "comment": comment,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        
        path = self._approval_path(task_id)
        atomic_write_json(path, decision)
    
    def clear_approval(self, task_id: str) -> None:
        """
        Clear approval decision (for retry/reset).
        
        Args:
            task_id: Task identifier
        """
        path = self._approval_path(task_id)
        if path.exists():
            path.unlink()
