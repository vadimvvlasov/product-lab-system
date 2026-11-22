"""validate_workflow checks env:NAME references in executor config."""

import pytest

from graph_engine.models.enums import VerificationMethod
from graph_engine.models.workflow import (
    ExecutionLimits,
    ExecutorConfig,
    TaskDefinition,
    VerificationCriterion,
    WorkflowDefinition,
    WorkflowMetadata,
)
from graph_engine.validation import validate_executor_env_refs, validate_workflow

BAD = ["env:FOO BAR", "env:1X", "env: DB_PWD", "env:DB_PWD\n", "env:", "env:$HOME", "env:A-B"]
GOOD = ["env:OPENAI_API_KEY", "env:DB_PWD", "env:_X", "env:a1"]


def make(config):
    return WorkflowDefinition(
        version="1",
        workflow=WorkflowMetadata(id="test", description="Test"),
        execution=ExecutionLimits(max_concurrency=1, max_retries=0),
        executors={"worker": ExecutorConfig(adapter="mock", config=config)},
        executor_mapping={},
        tasks=[
            TaskDefinition(
                id="t", type="work", executor="worker",
                verification=[
                    VerificationCriterion(id="c", method=VerificationMethod.COMMAND, command="true")
                ],
            )
        ],
    )


@pytest.mark.parametrize("value", BAD)
@pytest.mark.parametrize("key", ["api_key", "base_url"])
def test_bad_value_reported_for_secret_and_non_secret_keys(key, value):
    report = validate_workflow(make({key: value}))
    assert any(f"executor 'worker' config '{key}'" in e for e in report.errors)
    assert not report.is_valid


def test_message_wording():
    errors = validate_executor_env_refs(make({"api_key": "env:FOO BAR"}))
    assert errors == [
        "executor 'worker' config 'api_key': invalid environment variable name "
        "'FOO BAR' in 'env:FOO BAR'; expected [A-Za-z_][A-Za-z0-9_]*"
    ]


def test_nested_and_list_paths():
    errors = validate_executor_env_refs(
        make({"auth": {"token": "env:1X"}, "hosts": ["env:OK", "env:a b"]})
    )
    assert any("config 'auth.token'" in e for e in errors)
    assert any("config 'hosts[1]'" in e for e in errors)
    assert len(errors) == 2


@pytest.mark.parametrize("value", GOOD)
@pytest.mark.parametrize("key", ["api_key", "base_url"])
def test_valid_names_no_errors(key, value):
    assert validate_workflow(make({key: value})).errors == []


@pytest.mark.parametrize("value", ["https://x", "ENV:x", "prod"])
def test_non_env_strings_not_flagged(value):
    assert validate_executor_env_refs(make({"base_url": value})) == []


def test_mapping_keys_not_flagged():
    assert validate_executor_env_refs(make({"labels": {"env:a b": "x"}})) == []


def test_non_string_values_not_flagged():
    assert validate_executor_env_refs(make({"n": 5, "flag": True, "none": None})) == []


def test_non_env_values_not_echoed():
    errors = validate_executor_env_refs(make({"base_url": "env:a b", "other": "hunter2"}))
    assert all("hunter2" not in e for e in errors)
