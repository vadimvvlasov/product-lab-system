"""Validation report aggregation."""

from dataclasses import dataclass, field


@dataclass
class ValidationReport:
    """Aggregated validation results."""
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    topological_order: list[str] = field(default_factory=list)
    
    @property
    def is_valid(self) -> bool:
        """True if no errors."""
        return len(self.errors) == 0
    
    def format(self) -> str:
        """Format report as human-readable text."""
        lines = []
        
        if self.errors:
            lines.append(f"❌ Validation failed with {len(self.errors)} error(s):")
            for err in self.errors:
                lines.append(f"  - {err}")
        
        if self.warnings:
            lines.append(f"\n⚠️  {len(self.warnings)} warning(s):")
            for warn in self.warnings:
                lines.append(f"  - {warn}")
        
        if not self.errors and not self.warnings:
            lines.append("✅ Workflow is valid")
        
        if self.topological_order:
            lines.append(f"\n📋 Execution order: {' → '.join(self.topological_order)}")
        
        return "\n".join(lines)
