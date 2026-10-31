"""Artifact validation and publication."""

import hashlib
import os
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from graph_engine.errors import ArtifactError


@dataclass
class ArtifactRecord:
    """Published artifact metadata."""
    name: str
    path: str
    producer_task: str
    producer_attempt: int
    created_at: str
    size_bytes: int
    sha256: str
    validation_status: str = "valid"


class ArtifactManager:
    """Artifact validation and publication."""
    
    def __init__(self, run_root: Path):
        """
        Initialize artifact manager.
        
        Args:
            run_root: Run directory root
        """
        self.run_root = run_root
        self.artifacts_dir = run_root / "artifacts"
        self.staging_dir = self.artifacts_dir / ".staging"
    
    def validate_output(
        self,
        output_path: str,
        staging_root: Path,
        min_bytes: int = 1,
    ) -> ArtifactRecord:
        """
        Validate a staged output artifact.
        
        Args:
            output_path: Relative path (must start with artifacts/)
            staging_root: Staging directory root
            min_bytes: Minimum file size
            
        Returns:
            ArtifactRecord with metadata
            
        Raises:
            ArtifactError: if validation fails
        """
        # Compute staged file path
        if not output_path.startswith("artifacts/"):
            raise ArtifactError(
                f"Output path must start with 'artifacts/', got: {output_path}"
            )
        
        rel_path = output_path[len("artifacts/"):]
        staged_path = staging_root / "artifacts" / rel_path
        
        # Check existence
        if not staged_path.exists():
            raise ArtifactError(f"Artifact not found: {staged_path}")
        
        # Check it's a regular file
        if not staged_path.is_file():
            raise ArtifactError(f"Artifact is not a regular file: {staged_path}")
        
        # Check size
        size = staged_path.stat().st_size
        if size < min_bytes:
            raise ArtifactError(
                f"Artifact too small: {size} bytes < {min_bytes} (path: {staged_path})"
            )
        
        # Compute checksum
        sha256 = self._compute_checksum(staged_path)
        
        return ArtifactRecord(
            name="",  # Set by caller
            path=output_path,
            producer_task="",  # Set by caller
            producer_attempt=0,  # Set by caller
            created_at=datetime.now(timezone.utc).isoformat(),
            size_bytes=size,
            sha256=sha256,
        )
    
    def publish_artifact(
        self,
        staged_path: Path,
        target_path: str,
    ) -> str:
        """
        Publish artifact atomically.
        
        Uses os.replace for atomic move on same filesystem.
        
        Args:
            staged_path: Source file in staging
            target_path: Target relative path (artifacts/...)
            
        Returns:
            SHA-256 checksum of published file
            
        Raises:
            ArtifactError: if publication fails
        """
        if not target_path.startswith("artifacts/"):
            raise ArtifactError(f"Target path must start with 'artifacts/', got: {target_path}")
        
        final_path = self.run_root / target_path
        
        try:
            # Verify checksum before move
            checksum_before = self._compute_checksum(staged_path)
            
            # Create parent directories
            final_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Atomic move (same filesystem)
            os.replace(staged_path, final_path)
            
            # Verify after move
            checksum_after = self._compute_checksum(final_path)
            
            if checksum_before != checksum_after:
                raise ArtifactError(
                    f"Checksum mismatch after publication: "
                    f"{checksum_before} != {checksum_after}"
                )
            
            return checksum_after
            
        except Exception as e:
            raise ArtifactError(f"Failed to publish artifact: {e}") from e
    
    def copy_input_artifact(
        self,
        source_path: Path,
        target_dir: Path,
        artifact_name: str,
    ):
        """
        Copy an input artifact to staging directory.
        
        Args:
            source_path: Source artifact file
            target_dir: Target staging/inputs directory
            artifact_name: Artifact name (for subdirectory)
        """
        target_subdir = target_dir / "inputs" / artifact_name
        target_subdir.mkdir(parents=True, exist_ok=True)
        
        # Preserve relative structure if source is in a nested path
        target_file = target_subdir / source_path.name
        
        shutil.copy2(source_path, target_file)
    
    def _compute_checksum(self, path: Path) -> str:
        """Compute SHA-256 checksum of a file."""
        sha256 = hashlib.sha256()
        with open(path, 'rb') as f:
            while chunk := f.read(65536):
                sha256.update(chunk)
        return sha256.hexdigest()
