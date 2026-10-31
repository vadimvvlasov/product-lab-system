"""Shared test fixtures and utilities."""

import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test runs."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def workflow_factory(temp_dir):
    """Factory for creating test workflow files."""
    def _create(content: str, name: str = "test-workflow.yaml") -> Path:
        path = temp_dir / name
        path.write_text(content)
        return path
    return _create
