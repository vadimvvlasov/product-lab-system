"""Public API for graph engine integration."""

from pathlib import Path
from typing import Union

from graph_engine.models.workflow import WorkflowDefinition
from graph_engine.parser import parse_workflow, parse_workflow_file
from graph_engine.validation import ValidationReport, validate_workflow


def validate_workflow_file(workflow_path: Union[str, Path]) -> ValidationReport:
    """
    Load and validate a workflow file.
    
    This is the stable public API for workflow validation.
    
    Args:
        workflow_path: Path to workflow YAML file
        
    Returns:
        ValidationReport with errors, warnings, and topological order
        
    Example:
        >>> report = validate_workflow_file("workflow.yaml")
        >>> if not report.is_valid:
        ...     print(report.format())
    """
    path = Path(workflow_path)
    workflow, _ = parse_workflow_file(path)
    return validate_workflow(workflow)


__all__ = [
    "validate_workflow_file",
    "ValidationReport",
]
