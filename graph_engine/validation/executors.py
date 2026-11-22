"""Executor resolution and unused resource warnings."""

from graph_engine.env_refs import env_ref_error
from graph_engine.models.workflow import WorkflowDefinition


def validate_executor_env_refs(workflow: WorkflowDefinition) -> list[str]:
    """
    Check every string in executors.*.config that starts with `env:`.

    Applies to all keys (secret or not), at any depth. Mapping keys and
    non-string values are not checked. Returns a list of error messages.
    """
    errors: list[str] = []
    for name, executor in workflow.executors.items():
        _walk_env_refs(executor.config, "", f"executor '{name}'", errors)
    return errors


def _walk_env_refs(value, path: str, owner: str, errors: list[str]) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            _walk_env_refs(item, f"{path}.{key}" if path else str(key), owner, errors)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _walk_env_refs(item, f"{path}[{index}]", owner, errors)
    else:
        error = env_ref_error(value)
        if error:
            errors.append(f"{owner} config '{path}': {error}")


def resolve_executor(workflow: WorkflowDefinition, task_id: str) -> str:
    """
    Resolve executor name for a task.
    
    Priority: explicit task.executor > executor_mapping[task.type] > error
    
    Args:
        workflow: Workflow definition
        task_id: Task ID
        
    Returns:
        Executor name
        
    Raises:
        ValueError: if executor cannot be resolved
    """
    task = workflow.get_task(task_id)
    if not task:
        raise ValueError(f"Task '{task_id}' not found")
    
    if task.executor:
        return task.executor
    
    mapped = workflow.executor_mapping.get(task.type)
    if mapped:
        return mapped
    
    raise ValueError(
        f"task '{task_id}': cannot resolve executor "
        f"(no explicit executor, no mapping for type '{task.type}')"
    )


def check_unused_resources(workflow: WorkflowDefinition) -> list[str]:
    """
    Check for unused executors and mappings.
    
    Returns list of warning messages.
    """
    warnings = []
    
    # Collect used executors
    used_executors = set()
    used_mappings = set()
    
    for task in workflow.tasks:
        if task.executor:
            used_executors.add(task.executor)
        else:
            if task.type in workflow.executor_mapping:
                used_mappings.add(task.type)
                mapped_executor = workflow.executor_mapping[task.type]
                used_executors.add(mapped_executor)
        
        # Verification agent executors
        for crit in task.verification:
            if crit.executor:
                used_executors.add(crit.executor)
    
    # Check for unused
    for executor_name in workflow.executors:
        if executor_name not in used_executors:
            warnings.append(f"Executor '{executor_name}' is defined but never used")
    
    for task_type in workflow.executor_mapping:
        if task_type not in used_mappings:
            warnings.append(
                f"Executor mapping for type '{task_type}' is defined but never used"
            )
    
    return warnings
