"""Workflow validation."""

from graph_engine.validation.dag import validate_dag
from graph_engine.validation.executors import check_unused_resources, resolve_executor
from graph_engine.validation.references import validate_references
from graph_engine.validation.report import ValidationReport
from graph_engine.validation.schema import validate_schema


def validate_workflow(workflow) -> ValidationReport:
    """
    Run complete workflow validation.
    
    Args:
        workflow: Parsed WorkflowDefinition
        
    Returns:
        ValidationReport with errors, warnings, and topological order
    """
    report = ValidationReport()
    
    # Schema validation
    report.errors.extend(validate_schema(workflow))
    
    # Reference validation
    report.errors.extend(validate_references(workflow))
    
    # Stop here if basic validation failed
    if report.errors:
        return report
    
    # DAG validation and topological sort
    try:
        topo_order, _ = validate_dag(workflow)
        report.topological_order = topo_order
    except Exception as e:
        report.errors.append(str(e))
        return report
    
    # Warnings (unused resources)
    report.warnings.extend(check_unused_resources(workflow))
    
    return report


__all__ = [
    "validate_workflow",
    "ValidationReport",
    "validate_schema",
    "validate_references",
    "validate_dag",
    "resolve_executor",
    "check_unused_resources",
]
