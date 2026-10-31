"""Atomic file operations with fsync."""

import json
import os
import tempfile
from pathlib import Path
from typing import Any

from graph_engine.errors import PersistenceError


def atomic_write_json(path: Path, data: Any, indent: int = 2):
    """
    Write JSON atomically with fsync.
    
    Steps:
    1. Write to temp file in same directory
    2. Flush and fsync the file
    3. os.replace (atomic on POSIX)
    4. fsync the directory
    
    Args:
        path: Target file path
        data: JSON-serializable data
        indent: JSON indentation
        
    Raises:
        PersistenceError: if write fails
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        # Create temp file in same directory (same filesystem)
        fd, temp_path = tempfile.mkstemp(
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp"
        )
        
        try:
            # Write JSON
            with os.fdopen(fd, 'w') as f:
                json.dump(data, f, indent=indent, ensure_ascii=False)
                f.write('\n')  # Trailing newline
                f.flush()
                os.fsync(f.fileno())  # Force to disk
            
            # Atomic replace
            os.replace(temp_path, path)
            
            # Fsync directory to persist the rename
            dir_fd = os.open(path.parent, os.O_RDONLY)
            try:
                os.fsync(dir_fd)
            finally:
                os.close(dir_fd)
                
        except Exception:
            # Clean up temp file on error
            try:
                os.unlink(temp_path)
            except OSError:
                pass
            raise
            
    except Exception as e:
        raise PersistenceError(
            f"Failed to write {path}: {e}"
        ) from e


def atomic_read_json(path: Path) -> Any:
    """
    Read JSON file.
    
    Args:
        path: File path
        
    Returns:
        Parsed JSON data
        
    Raises:
        PersistenceError: if read fails
    """
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except Exception as e:
        raise PersistenceError(
            f"Failed to read {path}: {e}"
        ) from e


def atomic_append_jsonl(path: Path, record: dict):
    """
    Append a JSON record to a JSONL file.
    
    Args:
        path: JSONL file path
        record: Dict to append
        
    Raises:
        PersistenceError: if append fails
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(path, 'a') as f:
            f.write(json.dumps(record, ensure_ascii=False))
            f.write('\n')
            f.flush()
            os.fsync(f.fileno())
    except Exception as e:
        raise PersistenceError(
            f"Failed to append to {path}: {e}"
        ) from e
