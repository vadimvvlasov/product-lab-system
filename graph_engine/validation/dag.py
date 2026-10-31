"""DAG validation and topological sort."""

from collections import deque

from graph_engine.errors import DAGCycleError
from graph_engine.models.workflow import WorkflowDefinition


def validate_dag(workflow: WorkflowDefinition) -> tuple[list[str], list[str]]:
    """
    Validate workflow is a DAG and compute topological order.
    
    Uses Kahn's algorithm to detect cycles and produce deterministic ordering.
    
    Args:
        workflow: Validated workflow definition
        
    Returns:
        (topological_order, cycle_path)
        If no cycle: (ordered_task_ids, [])
        If cycle: ([], cycle_path)
        
    Raises:
        DAGCycleError: if workflow contains a cycle
    """
    # Build adjacency and in-degree
    task_ids = [t.id for t in workflow.tasks]
    in_degree = {t.id: len(t.depends_on) for t in workflow.tasks}
    children = {t.id: [] for t in workflow.tasks}
    
    for task in workflow.tasks:
        for dep in task.depends_on:
            if dep in children:  # Skip invalid deps (caught by references validation)
                children[dep].append(task.id)
    
    # Kahn's algorithm
    queue = deque([tid for tid in task_ids if in_degree[tid] == 0])
    order = []
    
    while queue:
        # Process in declaration order for determinism
        current = queue.popleft()
        order.append(current)
        
        for child in sorted(children[current]):  # Stable sort
            in_degree[child] -= 1
            if in_degree[child] == 0:
                queue.append(child)
    
    if len(order) != len(task_ids):
        # Cycle detected - find one cycle path
        cycle = _find_cycle(workflow)
        raise DAGCycleError(
            f"Workflow contains a cycle: {' -> '.join(cycle)}",
            cycle_path=cycle
        )
    
    return order, []


def _find_cycle(workflow: WorkflowDefinition) -> list[str]:
    """Find one cycle in the graph using DFS."""
    visited = set()
    rec_stack = set()
    path = []
    
    def dfs(task_id: str) -> bool:
        """Returns True if cycle found."""
        visited.add(task_id)
        rec_stack.add(task_id)
        path.append(task_id)
        
        task = workflow.get_task(task_id)
        if task:
            for dep in task.depends_on:
                if dep not in visited:
                    if dfs(dep):
                        return True
                elif dep in rec_stack:
                    # Found cycle
                    cycle_start = path.index(dep)
                    return True
        
        path.pop()
        rec_stack.remove(task_id)
        return False
    
    for task in workflow.tasks:
        if task.id not in visited:
            if dfs(task.id):
                # Extract cycle from path
                if path:
                    # Find where cycle closes
                    last = path[-1]
                    task_obj = workflow.get_task(last)
                    if task_obj:
                        for dep in task_obj.depends_on:
                            if dep in path:
                                cycle_start = path.index(dep)
                                return path[cycle_start:] + [dep]
                return path
    
    return []
