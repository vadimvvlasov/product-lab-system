"""Executor base protocol."""

from typing import Protocol

from graph_engine.execution.context import ExecutionContext
from graph_engine.execution.result import ExecutionResult


class Executor(Protocol):
    """
    Executor protocol for task execution.
    
    Executors are adapters that run tasks: AI agents, shell commands, etc.
    """
    
    name: str
    adapter: str
    
    def execute(self, context: ExecutionContext) -> ExecutionResult:
        """
        Execute a task.
        
        Args:
            context: Execution context with inputs, outputs, staging dir
            
        Returns:
            ExecutionResult with status, artifacts, metadata
        """
        ...
    
    def cancel(self) -> None:
        """
        Request cancellation (best-effort, cooperative).
        
        Optional operation. Executors may ignore if not supported.
        """
        ...
