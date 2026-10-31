"""Workflow and config snapshot management."""

import hashlib
import json
from pathlib import Path

from graph_engine.models.workflow import WorkflowDefinition


def compute_hash(data: bytes) -> str:
    """Compute SHA-256 hash of data."""
    return hashlib.sha256(data).hexdigest()


def snapshot_workflow(workflow_bytes: bytes, target: Path) -> str:
    """
    Save workflow YAML snapshot.
    
    Args:
        workflow_bytes: Original YAML bytes
        target: Target snapshot path
        
    Returns:
        SHA-256 hash of content
    """
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(workflow_bytes)
    return compute_hash(workflow_bytes)


def snapshot_executor_config(workflow: WorkflowDefinition, target: Path) -> str:
    """
    Save executor configuration snapshot.
    
    Normalizes config to remove secrets (replaces env:NAME references with placeholders).
    
    Args:
        workflow: Workflow definition
        target: Target snapshot path
        
    Returns:
        SHA-256 hash of normalized config
    """
    # Extract executor configs
    config_snapshot = {}
    for name, executor in workflow.executors.items():
        # Copy config, mask secrets (simplified - full version in Stage 8)
        normalized = {
            "adapter": executor.adapter,
            "config": _normalize_config(executor.config),
        }
        config_snapshot[name] = normalized
    
    # Write snapshot
    target.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(config_snapshot, indent=2, sort_keys=True).encode()
    target.write_bytes(content)
    
    return compute_hash(content)


def _normalize_config(config: dict) -> dict:
    """
    Normalize config for snapshot (mask secrets).
    
    Real implementation in Stage 8 will:
    - Detect env:NAME references
    - Reject literal secret keys
    - Store env var names, not values
    """
    # Placeholder: pass through for now
    return config.copy()


def verify_snapshot_hash(path: Path, expected_hash: str) -> bool:
    """Verify snapshot file matches expected hash."""
    if not path.exists():
        return False
    actual_hash = compute_hash(path.read_bytes())
    return actual_hash == expected_hash
