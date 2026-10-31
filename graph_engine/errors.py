"""Graph Engine error hierarchy."""

from typing import Optional


class GraphEngineError(Exception):
    """Base exception for all graph engine errors."""
    pass


class ValidationError(GraphEngineError):
    """Workflow validation failed."""
    pass


class WorkflowParseError(GraphEngineError):
    """Workflow file parsing failed."""
    pass


class DAGCycleError(ValidationError):
    """Workflow contains a cycle."""
    
    def __init__(self, message: str, cycle_path: Optional[list[str]] = None):
        super().__init__(message)
        self.cycle_path = cycle_path or []


class ExecutorError(GraphEngineError):
    """Executor-related error."""
    pass


class PersistenceError(GraphEngineError):
    """State persistence or recovery error."""
    pass


class ArtifactError(GraphEngineError):
    """Artifact validation or publication error."""
    pass


class RecoveryError(GraphEngineError):
    """Recovery reconciliation error."""
    pass
