"""Schema and structural validation."""

from pathlib import Path

from graph_engine.errors import ValidationError
from graph_engine.ids import is_safe_id
from graph_engine.models.enums import ApprovalRequirement, VerificationMethod
from graph_engine.models.workflow import TaskDefinition, WorkflowDefinition


def validate_schema(workflow: WorkflowDefinition) -> list[str]:
    """
    Validate workflow schema constraints.
    
    Returns list of error messages (empty if valid).
    """
    errors = []
    
    # Workflow ID
    if not is_safe_id(workflow.workflow.id):
        errors.append(
            f"workflow.id '{workflow.workflow.id}' must be filesystem-safe "
            "(alphanumeric, underscore, dash only)"
        )
    
    # Task IDs and artifact names
    for task in workflow.tasks:
        if not is_safe_id(task.id):
            errors.append(
                f"task '{task.id}' must be filesystem-safe "
                "(alphanumeric, underscore, dash only)"
            )
        
        # Output paths must start with artifacts/ and be relative
        for output in task.outputs:
            path = Path(output.path)
            
            if path.is_absolute():
                errors.append(
                    f"task '{task.id}' output '{output.name}': "
                    f"path must be relative, got absolute path '{output.path}'"
                )
            
            if not output.path.startswith("artifacts/"):
                errors.append(
                    f"task '{task.id}' output '{output.name}': "
                    f"path must start with 'artifacts/', got '{output.path}'"
                )
            
            if ".." in path.parts:
                errors.append(
                    f"task '{task.id}' output '{output.name}': "
                    f"path must not contain '..', got '{output.path}'"
                )
            
            if output.path.startswith("artifacts/.staging/"):
                errors.append(
                    f"task '{task.id}' output '{output.name}': "
                    f"path must not use .staging prefix, got '{output.path}'"
                )
        
        # Verification criteria requirements
        for crit in task.verification:
            if crit.method == VerificationMethod.COMMAND:
                if not crit.command:
                    errors.append(
                        f"task '{task.id}' criterion '{crit.id}': "
                        "command method requires 'command' field"
                    )
            elif crit.method == VerificationMethod.AGENT:
                if not crit.executor:
                    errors.append(
                        f"task '{task.id}' criterion '{crit.id}': "
                        "agent method requires 'executor' field"
                    )
                if not crit.acceptance_criteria:
                    errors.append(
                        f"task '{task.id}' criterion '{crit.id}': "
                        "agent method requires 'acceptance_criteria' field"
                    )
            elif crit.method == VerificationMethod.HUMAN:
                if not crit.prompt:
                    errors.append(
                        f"task '{task.id}' criterion '{crit.id}': "
                        "human method requires 'prompt' field"
                    )
        
        # Side effects validation
        if task.side_effects in ["idempotent", "unsafe"] and not task.idempotency_key:
            errors.append(
                f"task '{task.id}': side_effects '{task.side_effects.value}' "
                "requires 'idempotency_key'"
            )
    
    return errors
