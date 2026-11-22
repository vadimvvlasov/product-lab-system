"""Tests for executor config snapshots."""

import textwrap

import pytest

from graph_engine.errors import ExecutorError
from graph_engine.parser import parse_workflow
from graph_engine.persistence.snapshot import snapshot_executor_config

WORKFLOW = """\
version: "1"
workflow:
  id: snapshot-test
  description: Snapshot test
execution:
  max_concurrency: 1
  max_retries: 0
executors:
  worker:
    adapter: mock
    config:
{config}
executor_mapping: {{}}
tasks:
  - id: task-1
    type: work
    verification:
      - id: check
        method: command
        command: "true"
"""


def make_workflow(config: str):
    indented = textwrap.indent(textwrap.dedent(config).strip(), "      ")
    return parse_workflow(WORKFLOW.format(config=indented).encode())


def test_env_reference_is_kept_as_reference(tmp_path):
    workflow = make_workflow("api_key: env:OPENAI_API_KEY")
    target = tmp_path / "executor_config.json"

    snapshot_executor_config(workflow, target)

    content = target.read_text()
    assert "env:OPENAI_API_KEY" in content
    assert "sk-live" not in content


def test_literal_secret_is_rejected_and_not_written(tmp_path):
    workflow = make_workflow("api_key: sk-live-123456")
    target = tmp_path / "executor_config.json"

    with pytest.raises(ExecutorError, match="env:NAME"):
        snapshot_executor_config(workflow, target)

    assert not target.exists()


def test_nested_literal_secret_is_rejected(tmp_path):
    workflow = make_workflow(
        """
        headers:
          authorization: Bearer sk-live-123456
        """
    )

    with pytest.raises(ExecutorError, match="authorization"):
        snapshot_executor_config(workflow, tmp_path / "executor_config.json")


def test_non_secret_key_containing_token_is_allowed(tmp_path):
    workflow = make_workflow("max_tokens: 1024")
    target = tmp_path / "executor_config.json"

    snapshot_executor_config(workflow, target)

    assert '"max_tokens": 1024' in target.read_text()


@pytest.mark.parametrize(
    "key",
    ["apiKey", "secret_key", "API_KEY", "OPENAI_API_KEY", "PASSWORD", "api-key"],
)
def test_camel_case_and_secret_key_are_rejected(tmp_path, key):
    workflow = make_workflow(f"{key}: sk-live-123456")

    with pytest.raises(ExecutorError, match="env:NAME"):
        snapshot_executor_config(workflow, tmp_path / "executor_config.json")


def test_secret_in_list_is_rejected(tmp_path):
    workflow = make_workflow(
        """
        headers:
          - authorization: Bearer sk-live-123456
        """
    )

    with pytest.raises(ExecutorError, match="authorization"):
        snapshot_executor_config(workflow, tmp_path / "executor_config.json")


@pytest.mark.parametrize(
    "key",
    [
        "private_key", "privateKey", "PRIVATE_KEY", "apikey", "APIKEY", "ApiKey",
        "passwd", "PASSWD", "pwd", "PWD", "db_pwd", "user_passwd",
        "api_key", "token", "secret", "password", "credential", "authorization",
        "access_key", "accessKey", "ACCESS_KEY", "ACCESS-KEY", "access-key", "accesskey",
        "ssh_key", "sshKey", "SSH_KEY", "ssh-key", "sshkey",
        "aws_secret_access_key", "AWS_ACCESS_KEY", "deploy_ssh_key", "public_ssh_key",
    ],
)
def test_secret_key_variants_reject_literal(tmp_path, key):
    from graph_engine.persistence.snapshot import _looks_secret

    assert _looks_secret(key)
    workflow = make_workflow(f"{key}: literal-value")
    target = tmp_path / "executor_config.json"

    with pytest.raises(ExecutorError, match="env:NAME"):
        snapshot_executor_config(workflow, target)

    assert not target.exists()


@pytest.mark.parametrize(
    "key",
    ["max_tokens", "tokenizer", "keyboard", "token_count", "monkey", "pwdfile",
     "cache_key", "sort_key",
     "access_key_id", "accessKeyId", "AWS_ACCESS_KEY_ID", "ssh_key_path", "ssh_key_file",
     "ssh_keys", "access_keyboard", "bypass_key", "my_accesskeyname", "ssh_public_key"],
)
def test_non_secret_keys_accept_literal(tmp_path, key):
    workflow = make_workflow(f"{key}: literal-value")
    target = tmp_path / "executor_config.json"

    snapshot_executor_config(workflow, target)

    assert "literal-value" in target.read_text()


@pytest.mark.parametrize("value", ['"env:"', '"env: "', '"env:   "', "null", "5", "[a, b]"])
def test_secret_key_rejects_empty_env_and_non_strings(tmp_path, value):
    workflow = make_workflow(f"api_key: {value}")
    target = tmp_path / "executor_config.json"

    with pytest.raises(ExecutorError, match="env:NAME"):
        snapshot_executor_config(workflow, target)

    assert not target.exists()


def test_secret_key_env_reference_kept_verbatim(tmp_path):
    workflow = make_workflow("pwd: env:DB_PWD")
    target = tmp_path / "executor_config.json"

    snapshot_executor_config(workflow, target)

    assert "env:DB_PWD" in target.read_text()


@pytest.mark.parametrize(
    "line, reference",
    [("access_key: env:AWS_ACCESS_KEY", "env:AWS_ACCESS_KEY"),
     ("sshKey: env:DEPLOY_KEY", "env:DEPLOY_KEY")],
)
def test_new_secret_keys_env_reference_kept_verbatim(tmp_path, line, reference):
    workflow = make_workflow(line)
    target = tmp_path / "executor_config.json"

    snapshot_executor_config(workflow, target)

    assert reference in target.read_text()


def test_nested_ssh_key_rejects_literal_without_writing(tmp_path):
    workflow = make_workflow("ssh:\n  ssh_key: literal")
    target = tmp_path / "executor_config.json"

    with pytest.raises(ExecutorError, match="env:NAME"):
        snapshot_executor_config(workflow, target)

    assert not target.exists()
