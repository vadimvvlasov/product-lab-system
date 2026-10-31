"""Test artifact manager."""

import pytest

from graph_engine.artifacts import ArtifactManager
from graph_engine.errors import ArtifactError


def test_validate_output_success(temp_dir):
    """Validate an existing output artifact."""
    # Create staging structure
    staging_root = temp_dir / "staging"
    artifact_file = staging_root / "artifacts" / "output.txt"
    artifact_file.parent.mkdir(parents=True)
    artifact_file.write_text("test content")
    
    manager = ArtifactManager(temp_dir)
    record = manager.validate_output("artifacts/output.txt", staging_root, min_bytes=5)
    
    assert record.path == "artifacts/output.txt"
    assert record.size_bytes == 12
    assert len(record.sha256) == 64


def test_validate_output_missing_file(temp_dir):
    """Validation fails if file doesn't exist."""
    manager = ArtifactManager(temp_dir)
    staging_root = temp_dir / "staging"
    
    with pytest.raises(ArtifactError, match="not found"):
        manager.validate_output("artifacts/missing.txt", staging_root)


def test_validate_output_too_small(temp_dir):
    """Validation fails if file is too small."""
    staging_root = temp_dir / "staging"
    artifact_file = staging_root / "artifacts" / "small.txt"
    artifact_file.parent.mkdir(parents=True)
    artifact_file.write_text("x")
    
    manager = ArtifactManager(temp_dir)
    
    with pytest.raises(ArtifactError, match="too small"):
        manager.validate_output("artifacts/small.txt", staging_root, min_bytes=100)


def test_publish_artifact(temp_dir):
    """Publish artifact atomically."""
    # Setup staging
    staging_root = temp_dir / "staging"
    staged_file = staging_root / "artifacts" / "result.txt"
    staged_file.parent.mkdir(parents=True)
    staged_file.write_text("final result")
    
    # Publish
    manager = ArtifactManager(temp_dir)
    checksum = manager.publish_artifact(staged_file, "artifacts/result.txt")
    
    # Verify published
    published = temp_dir / "artifacts" / "result.txt"
    assert published.exists()
    assert published.read_text() == "final result"
    assert not staged_file.exists()  # Moved, not copied
    assert len(checksum) == 64


def test_copy_input_artifact(temp_dir):
    """Copy input artifact to staging."""
    # Source artifact
    source = temp_dir / "artifacts" / "input.txt"
    source.parent.mkdir()
    source.write_text("input data")
    
    # Copy to staging
    target_dir = temp_dir / "staging" / "task-1"
    manager = ArtifactManager(temp_dir)
    manager.copy_input_artifact(source, target_dir, "input-data")
    
    # Verify copied
    copied = target_dir / "inputs" / "input-data" / "input.txt"
    assert copied.exists()
    assert copied.read_text() == "input data"
