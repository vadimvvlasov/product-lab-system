"""Executor registry and factory."""

from graph_engine.errors import ExecutorError
from graph_engine.executors.mock import MockExecutor, MockExecutorConfig
from graph_engine.models.enums import ExecutionStatus
from graph_engine.models.workflow import ExecutorConfig, WorkflowDefinition


class ExecutorRegistry:
    """
    Executor factory and registry.
    
    Builds executors from workflow configuration deterministically.
    """
    
    def __init__(self, workflow: WorkflowDefinition):
        """
        Initialize registry from workflow.
        
        Args:
            workflow: Workflow definition
        """
        self.workflow = workflow
        self._executors: dict[str, any] = {}
    
    def get_executor(self, executor_name: str):
        """
        Get or create executor by name.
        
        Args:
            executor_name: Name from workflow executors section
            
        Returns:
            Executor instance
            
        Raises:
            ExecutorError: if executor cannot be created
        """
        if executor_name in self._executors:
            return self._executors[executor_name]
        
        if executor_name not in self.workflow.executors:
            raise ExecutorError(f"Executor '{executor_name}' not defined")
        
        executor_config = self.workflow.executors[executor_name]
        executor = self._create_executor(executor_name, executor_config)
        self._executors[executor_name] = executor
        
        return executor
    
    def _create_executor(self, name: str, config: ExecutorConfig):
        """
        Create executor instance.
        
        Args:
            name: Executor name
            config: Executor configuration
            
        Returns:
            Executor instance
            
        Raises:
            ExecutorError: if adapter is unknown
        """
        adapter = config.adapter
        
        if adapter == "mock":
            return self._create_mock_executor(name, config.config)
        
        # Stage 8: command, opencode adapters
        raise ExecutorError(
            f"Unknown adapter '{adapter}' for executor '{name}' "
            "(only 'mock' supported in Stage 3)"
        )
    
    def _create_mock_executor(self, name: str, config: dict) -> MockExecutor:
        """Create mock executor from config."""
        mock_config = MockExecutorConfig(
            result_status=ExecutionStatus(config.get("status", "success")),
            result_summary=config.get("summary", "Mock execution"),
            result_artifacts=config.get("artifacts", []),
            result_error=config.get("error"),
            delay_seconds=config.get("delay_seconds", 0.0),
            create_artifacts=config.get("create_artifacts", True),
            report_usage=config.get("report_usage", True),
            input_tokens=config.get("input_tokens", 100),
            output_tokens=config.get("output_tokens", 50),
        )
        
        return MockExecutor(name, mock_config)
