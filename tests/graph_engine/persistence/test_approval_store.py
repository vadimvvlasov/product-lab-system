"""Tests for human approval persistence."""

import json

import pytest

from graph_engine.persistence.approval_store import ApprovalStore


def test_record_and_get_approval(tmp_path):
    store = ApprovalStore(tmp_path)

    store.record_approval("task-a", True, approver="owner", comment="ok")

    decision = store.get_approval("task-a")
    assert decision["approved"] is True
    assert decision["approver"] == "owner"
    assert decision["comment"] == "ok"


def test_approval_requires_real_boolean(tmp_path):
    store = ApprovalStore(tmp_path)

    with pytest.raises(ValueError):
        store.record_approval("task-a", "false")


@pytest.mark.parametrize("task_id", ["../escape", "a/b", "", "a b"])
def test_rejects_unsafe_task_ids(tmp_path, task_id):
    store = ApprovalStore(tmp_path)

    with pytest.raises(ValueError):
        store.record_approval(task_id, True)
    with pytest.raises(ValueError):
        store.get_approval(task_id)


def test_clear_approval(tmp_path):
    store = ApprovalStore(tmp_path)
    store.record_approval("task-a", True)

    store.clear_approval("task-a")

    assert store.get_approval("task-a") is None


def test_invalid_json_is_not_an_approval(tmp_path):
    store = ApprovalStore(tmp_path)
    (tmp_path / "approvals" / "task-a.json").write_text("not json")

    assert store.get_approval("task-a") is None
