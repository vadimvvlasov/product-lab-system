---
name: UV Package Manager
description: Use uv for Python package management and test execution
inclusion: auto
---

# UV Package Manager Usage

This project uses `uv` for Python package management instead of `pip`.

## Installation Commands

Always use `uv` instead of `pip`:

```bash
# Install package in editable mode
uv pip install -e .

# Install with dev dependencies
uv pip install -e ".[dev]"

# Reinstall after code changes
uv pip install -e . --no-deps
```

## Running Tests

Activate the virtual environment before running pytest:

```bash
# Activate venv and run tests
source .venv/bin/activate && pytest tests/graph_engine/verification/ -v

# Or use venv directly
.venv/bin/pytest tests/graph_engine/verification/ -v
```

## Virtual Environment

The project uses a local `.venv` directory:

```bash
# Create fresh venv
uv venv --clear

# Install dependencies
uv pip install -e ".[dev]"
```

## Important Notes

- Always use `uv pip` instead of plain `pip`
- Activate `.venv` before running tests or scripts
- Reinstall package after adding new modules
- Use `--no-deps` flag when only code changed (not dependencies)
