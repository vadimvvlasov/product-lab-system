"""Tests for human approval verification."""

import pytest
from pathlib import Path

from graph_engine.verification.base import (
    VerificationCriterion,
    VerificationMethod,
    VerificationStatus,
)
from graph_engine.verification.human import HumanVerifier
from graph_engine.persistence.approval_store import ApprovalStore


@pytest.fixture
def approval_store(tmp_path):
    """Create approval store."""
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    return ApprovalStore(run_dir)


@pytest.fixture
def temp_staging(tmp_path):
    """Create temporary staging directory."""
    staging = tmp_path / "staging"
    staging.mkdir()
    return staging


def test_approval_pending_when_no_decision(approval_store, temp_staging):
    """Test PENDING status when no approval decision exists."""
    verifier = HumanVerifier(approval_store)
    
    criterion = VerificationCriterion(
        id="owner_signoff",
        method=VerificationMethod.HUMAN,
        prompt="Approve the deliverable",
    )
    
    task_context = {"task_id": "task1"}
    
    result = verifier.verify(criterion, temp_staging, task_context)
    
    assert result.status == VerificationStatus.PENDING
    assert "awaiting approval" in result.message.lower()


def test_approval_pass_when_approved(approval_store, temp_staging):
    """Test PASS status when approved."""
    # Record approval
    approval_store.record_approval(
        task_id="task1",
        approved=True,
        approver="alice",
        comment="Looks good",
    )
    
    verifier = HumanVerifier(approval_store)
    
    criterion = VerificationCriterion(
        id="owner_signoff",
        method=VerificationMethod.HUMAN,
        prompt="Approve the deliverable",
    )
    
    task_context = {"task_id": "task1"}
    
    result = verifier.verify(criterion, temp_staging, task_context)
    
    assert result.status == VerificationStatus.PASS
    assert result.approver == "alice"
    assert result.approval_comment == "Looks good"


def test_approval_fail_when_rejected(approval_store, temp_staging):
    """Test FAIL status when rejected."""
    # Record rejection
    approval_store.record_approval(
        task_id="task1",
        approved=False,
        approver="bob",
        comment="Needs changes",
    )
    
    verifier = HumanVerifier(approval_store)
    
    criterion = VerificationCriterion(
        id="owner_signoff",
        method=VerificationMethod.HUMAN,
    )
    
    task_context = {"task_id": "task1"}
    
    result = verifier.verify(criterion, temp_staging, task_context)
    
    assert result.status == VerificationStatus.FAIL
    assert result.approver == "bob"
    assert result.approval_comment == "Needs changes"


def test_approval_default_prompt(approval_store, temp_staging):
    """Test default prompt text."""
    verifier = HumanVerifier(approval_store)
    
    criterion = VerificationCriterion(
        id="approval",
        method=VerificationMethod.HUMAN,
        prompt=None,  # No custom prompt
    )
    
    task_context = {"task_id": "task1"}
    
    result = verifier.verify(criterion, temp_staging, task_context)
    
    assert result.status == VerificationStatus.PENDING
    assert "approve" in result.message.lower()
