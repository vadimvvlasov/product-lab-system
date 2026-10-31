"""Reference and dependency validation."""

from graph_engine.models.workflow import WorkflowDefinition


def validate_references(workflow: WorkflowDefinition) -> list[str]:
    """
    Validate all references (dependencies, inputs, executors, mappings).
    
    Returns list of error messages (empty if valid).
    """
    errors = []
    
    # Build task ID set
    task_ids = {t.id for t in workflow.tasks}
    
    # Check for duplicate task IDs
    if len(task_ids) != len(workflow.tasks):
        seen = set()
        for task in workflow.tasks:
            if task.id in seen:
                errors.append(f"Duplicate task ID: '{task.id}'")
            seen.add(task.id)
    
    # Check dependencies and inputs
    for task in workflow.tasks:
        # Self-dependency
        if task.id in task.depends_on:
            errors.append(f"task '{task.id}': self-dependency not allowed")
        
        # Non-existent dependencies
        for dep in task.depends_on:
            if dep not in task_ids:
                errors.append(
                    f"task '{task.id}' depends_on unknown task '{dep}'"
                )
        
        # Input sources must be direct dependencies
        for inp in task.inputs:
            if inp.from_task not in task.depends_on:
                errors.append(
                    f"task '{task.id}' input '{inp.name}': "
                    f"from_task '{inp.from_task}' is not in depends_on"
                )
            
            # Check that source task exists and declares the artifact
            source_task = workflow.get_task(inp.from_task)
            if source_task:
                artifact_names = {o.name for o in source_task.outputs}
                if inp.artifact not in artifact_names:
                    errors.append(
                        f"task '{task.id}' input '{inp.name}': "
                        f"task '{inp.from_task}' does not declare output artifact '{inp.artifact}'"
                    )
        
        # Artifact names must be unique within a task
        artifact_names = [o.name for o in task.outputs]
        if len(artifact_names) != len(set(artifact_names)):
            duplicates = [name for name in artifact_names if artifact_names.count(name) > 1]
            errors.append(
                f"task '{task.id}': duplicate output artifact names: {sorted(set(duplicates))}"
            )
    
    # Output paths must be unique across all tasks
    output_paths = {}
    for task in workflow.tasks:
        for output in task.outputs:
            if output.path in output_paths:
                errors.append(
                    f"Duplicate output path '{output.path}' in tasks "
                    f"'{output_paths[output.path]}' and '{task.id}'"
                )
            else:
                output_paths[output.path] = task.id
    
    # Executor resolution
    for task in workflow.tasks:
        # Explicit executor wins
        if task.executor:
            if task.executor not in workflow.executors:
                errors.append(
                    f"task '{task.id}': explicit executor '{task.executor}' not defined"
                )
        else:
            # Try mapping
            mapped_executor = workflow.executor_mapping.get(task.type)
            if not mapped_executor:
                errors.append(
                    f"task '{task.id}': no explicit executor and no mapping for type '{task.type}'"
                )
            elif mapped_executor not in workflow.executors:
                errors.append(
                    f"task '{task.id}': mapped executor '{mapped_executor}' "
                    f"(from type '{task.type}') not defined"
                )
        
        # Verification agent executors
        for crit in task.verification:
            if crit.executor and crit.executor not in workflow.executors:
                errors.append(
                    f"task '{task.id}' criterion '{crit.id}': "
                    f"executor '{crit.executor}' not defined"
                )
    
    # Check mapping targets
    for task_type, executor_name in workflow.executor_mapping.items():
        if executor_name not in workflow.executors:
            errors.append(
                f"executor_mapping['{task_type}']: executor '{executor_name}' not defined"
            )
    
    return errors
