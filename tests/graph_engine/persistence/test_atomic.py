"""Test atomic file operations."""

import json

from graph_engine.persistence.atomic import (
    atomic_append_jsonl,
    atomic_read_json,
    atomic_write_json,
)


def test_atomic_write_and_read(temp_dir):
    """Atomic write and read."""
    path = temp_dir / "test.json"
    data = {"key": "value", "num": 42}
    
    atomic_write_json(path, data)
    assert path.exists()
    
    loaded = atomic_read_json(path)
    assert loaded == data


def test_atomic_write_creates_parent(temp_dir):
    """Atomic write creates parent directories."""
    path = temp_dir / "nested" / "dir" / "file.json"
    atomic_write_json(path, {"test": True})
    
    assert path.exists()
    assert atomic_read_json(path) == {"test": True}


def test_atomic_write_overwrites(temp_dir):
    """Atomic write overwrites existing file."""
    path = temp_dir / "test.json"
    
    atomic_write_json(path, {"v": 1})
    atomic_write_json(path, {"v": 2})
    
    assert atomic_read_json(path) == {"v": 2}


def test_atomic_append_jsonl(temp_dir):
    """Append records to JSONL."""
    path = temp_dir / "events.jsonl"
    
    atomic_append_jsonl(path, {"event": "started"})
    atomic_append_jsonl(path, {"event": "completed"})
    
    lines = path.read_text().strip().split("\n")
    assert len(lines) == 2
    assert json.loads(lines[0]) == {"event": "started"}
    assert json.loads(lines[1]) == {"event": "completed"}
