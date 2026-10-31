"""Mock executor for testing."""

import time
from dataclasses import dataclass, field
from pathlib import Path
from threading import Event
from typing import Optional

from graph_engine.execution.context import ExecutionContext
from graph_engine.execution.result import ExecutionResult, Usage
from graph_engine.models.enums import ExecutionStatus


@dataclass
class MockExecutorConfig:
    """Configuration for mock executor behavior."""
    
    # Scripted result
    result_status: ExecutionStatus = ExecutionStatus.SUCCESS
    result_summary: str = "Mock execution completed"
    result_artifacts: list[str] = field(default_factory=list)
    result_error: Optional[str] = None
    
    # Simulation
    delay_seconds: float = 0.0
    create_artifacts: bool = True
    
    # Usage reporting
    report_usage: bool = True
    input_tokens: int = 100
    output_tokens: int = 50


class MockExecutor:
    """
    Mock executor for deterministic testing.
    
    Allows scripting results, delays, and synchronization.
    """
    
    def __init__(self, name: str, config: MockExecutorConfig):
        """
        Initialize mock executor.
        
        Args:
            name: Executor name
            config: Mock behavior configuration
        """
        self.name = name
        self.adapter = "mock"
        self.config = config
        
        # Call tracking
        self.call_count = 0
        self.last_context: Optional[ExecutionContext] = None
        self.calls: list[ExecutionContext] = []
        
        # Synchronization
        self._cancel_event = Event()
    
    def execute(self, context: ExecutionContext) -> ExecutionResult:
        """Execute mock task."""
        self.call_count += 1
        self.last_context = context
        self.calls.append(context)
        
        # Simulate delay
        if self.config.delay_seconds > 0:
            time.sleep(self.config.delay_seconds)
        
        # Check cancellation
        if self._cancel_event.is_set():
            return ExecutionResult(
                status=ExecutionStatus.CANCELLED,
                summary="Execution was cancelled",
            )
        
        # Create artifacts if configured
        if self.config.create_artifacts and self.config.result_status == ExecutionStatus.SUCCESS:
            for artifact_name in self.config.result_artifacts:
                # Find output path
                if artifact_name in context.required_outputs:
                    output_path = context.required_outputs[artifact_name]
                    artifact_file = context.staging_dir / output_path
                    artifact_file.parent.mkdir(parents=True, exist_ok=True)
                    artifact_file.write_text(f"Mock output for {artifact_name}\n")
        
        # Build usage
        usage = None
        if self.config.report_usage:
            usage = Usage(
                input_tokens=self.config.input_tokens,
                output_tokens=self.config.output_tokens,
                estimated_cost=0.001,
                available=True,
            )
        
        return ExecutionResult(
            status=self.config.result_status,
            summary=self.config.result_summary,
            artifacts=self.config.result_artifacts,
            usage=usage,
            error=self.config.result_error,
            metadata={"mock": True, "call_count": self.call_count},
        )
    
    def cancel(self):
        """Signal cancellation."""
        self._cancel_event.set()
    
    def reset(self):
        """Reset call tracking."""
        self.call_count = 0
        self.last_context = None
        self.calls = []
        self._cancel_event.clear()
