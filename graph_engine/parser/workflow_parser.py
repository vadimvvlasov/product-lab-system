"""Workflow YAML parser."""

from pathlib import Path
from typing import Any

from graph_engine.errors import WorkflowParseError
from graph_engine.models.enums import (
    ApprovalPoint,
    ApprovalRequirement,
    SideEffects,
    VerificationMethod,
)
from graph_engine.models.workflow import (
    ContextReference,
    ExecutionLimits,
    ExecutorConfig,
    TaskDefinition,
    TaskInput,
    TaskOutput,
    VerificationCriterion,
    WorkflowDefinition,
    WorkflowMetadata,
)
from graph_engine.parser.yaml_loader import load_yaml


def parse_workflow_file(path: Path) -> tuple[WorkflowDefinition, bytes]:
    """
    Parse a workflow YAML file.
    
    Args:
        path: Path to workflow file
        
    Returns:
        (WorkflowDefinition, raw_bytes) tuple
        
    Raises:
        WorkflowParseError: if file cannot be read or parsed
    """
    try:
        content = path.read_bytes()
    except OSError as e:
        raise WorkflowParseError(f"Cannot read workflow file: {e}") from e
    
    return parse_workflow(content), content


def parse_workflow(content: bytes) -> WorkflowDefinition:
    """
    Parse workflow from YAML bytes.
    
    Args:
        content: YAML content
        
    Returns:
        Parsed WorkflowDefinition
        
    Raises:
        WorkflowParseError: if content is invalid
    """
    data = load_yaml(content)
    
    if not isinstance(data, dict):
        raise WorkflowParseError(f"Workflow root must be a mapping, got {type(data).__name__}")
    
    # Check version
    version = data.get("version")
    if version != "1":
        raise WorkflowParseError(
            f"Unsupported workflow version: {version!r} (expected '1')"
        )
    
    # Parse workflow metadata
    workflow_data = data.get("workflow")
    if not isinstance(workflow_data, dict):
        raise WorkflowParseError("Missing or invalid 'workflow' section")
    
    workflow = WorkflowMetadata(
        id=_require_str(workflow_data, "workflow.id"),
        description=_require_str(workflow_data, "workflow.description"),
    )
    
    # Parse execution limits
    exec_data = data.get("execution")
    if not isinstance(exec_data, dict):
        raise WorkflowParseError("Missing or invalid 'execution' section")
    
    execution = ExecutionLimits(
        max_concurrency=_require_int(exec_data, "execution.max_concurrency", min_val=1),
        max_retries=_require_int(exec_data, "execution.max_retries", min_val=0),
        max_run_duration_minutes=_optional_int(exec_data, "execution.max_run_duration_minutes", min_val=1),
    )
    
    # Parse executors
    executors_data = data.get("executors", {})
    if not isinstance(executors_data, dict):
        raise WorkflowParseError("'executors' must be a mapping")
    
    executors = {}
    for name, exec_config in executors_data.items():
        if not isinstance(exec_config, dict):
            raise WorkflowParseError(f"executors.{name} must be a mapping")
        
        adapter = exec_config.get("adapter")
        if not isinstance(adapter, str) or not adapter:
            raise WorkflowParseError(f"executors.{name}.adapter must be a non-empty string")
        
        config = exec_config.get("config", {})
        if not isinstance(config, dict):
            raise WorkflowParseError(f"executors.{name}.config must be a mapping")
        
        executors[name] = ExecutorConfig(adapter=adapter, config=config)
    
    # Parse executor mapping
    mapping_data = data.get("executor_mapping", {})
    if not isinstance(mapping_data, dict):
        raise WorkflowParseError("'executor_mapping' must be a mapping")
    
    executor_mapping = {}
    for task_type, executor_name in mapping_data.items():
        if not isinstance(executor_name, str):
            raise WorkflowParseError(f"executor_mapping.{task_type} must be a string")
        executor_mapping[task_type] = executor_name
    
    # Parse tasks
    tasks_data = data.get("tasks")
    if not isinstance(tasks_data, list) or len(tasks_data) == 0:
        raise WorkflowParseError("'tasks' must be a non-empty list")
    
    tasks = []
    for idx, task_data in enumerate(tasks_data):
        if not isinstance(task_data, dict):
            raise WorkflowParseError(f"tasks[{idx}] must be a mapping")
        
        tasks.append(_parse_task(task_data, idx))
    
    # Parse context (optional)
    context = None
    context_data = data.get("context")
    if context_data is not None:
        if not isinstance(context_data, dict):
            raise WorkflowParseError("'context' must be a mapping")
        
        instructions = context_data.get("instructions", [])
        references = context_data.get("references", [])
        
        if not isinstance(instructions, list):
            raise WorkflowParseError("context.instructions must be a list")
        if not isinstance(references, list):
            raise WorkflowParseError("context.references must be a list")
        
        if not all(isinstance(i, str) for i in instructions):
            raise WorkflowParseError("context.instructions must contain only strings")
        if not all(isinstance(r, str) for r in references):
            raise WorkflowParseError("context.references must contain only strings")
        
        context = ContextReference(instructions=instructions, references=references)
    
    return WorkflowDefinition(
        version=version,
        workflow=workflow,
        execution=execution,
        executors=executors,
        executor_mapping=executor_mapping,
        tasks=tasks,
        context=context,
    )


def _parse_task(data: dict, idx: int) -> TaskDefinition:
    """Parse a single task definition."""
    prefix = f"tasks[{idx}]"
    
    task_id = _require_str(data, f"{prefix}.id")
    task_type = _require_str(data, f"{prefix}.type")
    
    # Parse dependencies
    depends_on = data.get("depends_on", [])
    if not isinstance(depends_on, list):
        raise WorkflowParseError(f"{prefix}.depends_on must be a list")
    if not all(isinstance(d, str) for d in depends_on):
        raise WorkflowParseError(f"{prefix}.depends_on must contain only strings")
    
    # Parse inputs
    inputs_data = data.get("inputs", [])
    if not isinstance(inputs_data, list):
        raise WorkflowParseError(f"{prefix}.inputs must be a list")
    
    inputs = []
    for i_idx, inp in enumerate(inputs_data):
        if not isinstance(inp, dict):
            raise WorkflowParseError(f"{prefix}.inputs[{i_idx}] must be a mapping")
        
        inputs.append(TaskInput(
            name=_require_str(inp, f"{prefix}.inputs[{i_idx}].name"),
            from_task=_require_str(inp, f"{prefix}.inputs[{i_idx}].from"),
            artifact=_require_str(inp, f"{prefix}.inputs[{i_idx}].artifact"),
        ))
    
    # Parse outputs
    outputs_data = data.get("outputs", [])
    if not isinstance(outputs_data, list):
        raise WorkflowParseError(f"{prefix}.outputs must be a list")
    
    outputs = []
    for o_idx, out in enumerate(outputs_data):
        if not isinstance(out, dict):
            raise WorkflowParseError(f"{prefix}.outputs[{o_idx}] must be a mapping")
        
        outputs.append(TaskOutput(
            name=_require_str(out, f"{prefix}.outputs[{o_idx}].name"),
            path=_require_str(out, f"{prefix}.outputs[{o_idx}].path"),
            min_bytes=_optional_int(out, f"{prefix}.outputs[{o_idx}].min_bytes", min_val=0) or 1,
        ))
    
    # Parse verification
    verification_data = data.get("verification", [])
    if not isinstance(verification_data, list) or len(verification_data) == 0:
        raise WorkflowParseError(f"{prefix}.verification must be a non-empty list")
    
    verification = []
    for v_idx, crit in enumerate(verification_data):
        if not isinstance(crit, dict):
            raise WorkflowParseError(f"{prefix}.verification[{v_idx}] must be a mapping")
        
        verification.append(_parse_verification_criterion(crit, f"{prefix}.verification[{v_idx}]"))
    
    # Parse approval
    approval_str = data.get("approval", "not_required")
    try:
        approval = ApprovalRequirement(approval_str)
    except ValueError:
        raise WorkflowParseError(
            f"{prefix}.approval must be 'required' or 'not_required', got {approval_str!r}"
        )
    
    approval_point_str = data.get("approval_point", "before_publish")
    try:
        approval_point = ApprovalPoint(approval_point_str)
    except ValueError:
        raise WorkflowParseError(
            f"{prefix}.approval_point must be 'before_execution' or 'before_publish', "
            f"got {approval_point_str!r}"
        )
    
    # Parse side effects
    side_effects_str = data.get("side_effects", "none")
    try:
        side_effects = SideEffects(side_effects_str)
    except ValueError:
        raise WorkflowParseError(
            f"{prefix}.side_effects must be 'none', 'idempotent', or 'unsafe', "
            f"got {side_effects_str!r}"
        )
    
    return TaskDefinition(
        id=task_id,
        type=task_type,
        executor=data.get("executor"),
        depends_on=depends_on,
        inputs=inputs,
        outputs=outputs,
        verification=verification,
        approval=approval,
        approval_point=approval_point,
        max_retries=_optional_int(data, f"{prefix}.max_retries", min_val=0),
        timeout_minutes=_optional_int(data, f"{prefix}.timeout_minutes", min_val=1),
        side_effects=side_effects,
        idempotency_key=data.get("idempotency_key"),
    )


def _parse_verification_criterion(data: dict, prefix: str) -> VerificationCriterion:
    """Parse a verification criterion."""
    crit_id = _require_str(data, f"{prefix}.id")
    
    method_str = _require_str(data, f"{prefix}.method")
    try:
        method = VerificationMethod(method_str)
    except ValueError:
        raise WorkflowParseError(
            f"{prefix}.method must be 'command', 'agent', or 'human', got {method_str!r}"
        )
    
    return VerificationCriterion(
        id=crit_id,
        method=method,
        command=data.get("command"),
        timeout_seconds=_optional_int(data, f"{prefix}.timeout_seconds", min_val=1) or 300,
        executor=data.get("executor"),
        acceptance_criteria=data.get("acceptance_criteria"),
        prompt=data.get("prompt"),
    )


def _require_str(data: dict, path: str) -> str:
    """Require a non-empty string field."""
    parts = path.split(".")
    value = data.get(parts[-1])
    
    if not isinstance(value, str) or not value:
        raise WorkflowParseError(f"'{path}' is required and must be a non-empty string")
    
    return value


def _require_int(data: dict, path: str, min_val: int | None = None) -> int:
    """Require an integer field."""
    parts = path.split(".")
    value = data.get(parts[-1])
    
    if not isinstance(value, int):
        raise WorkflowParseError(f"'{path}' must be an integer")
    
    if min_val is not None and value < min_val:
        raise WorkflowParseError(f"'{path}' must be >= {min_val}, got {value}")
    
    return value


def _optional_int(data: dict, path: str, min_val: int | None = None) -> int | None:
    """Optional integer field."""
    parts = path.split(".")
    value = data.get(parts[-1])
    
    if value is None:
        return None
    
    if not isinstance(value, int):
        raise WorkflowParseError(f"'{path}' must be an integer or omitted")
    
    if min_val is not None and value < min_val:
        raise WorkflowParseError(f"'{path}' must be >= {min_val}, got {value}")
    
    return value
