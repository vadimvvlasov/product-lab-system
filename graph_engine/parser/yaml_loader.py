"""YAML loader with duplicate key detection."""

import yaml
from typing import Any

from graph_engine.errors import WorkflowParseError


class SafeLoaderWithDuplicateCheck(yaml.SafeLoader):
    """SafeLoader that rejects duplicate mapping keys."""
    
    def construct_mapping(self, node, deep=False):
        """Override to detect duplicate keys."""
        if not isinstance(node, yaml.MappingNode):
            raise WorkflowParseError(
                f"Expected a mapping node, got {type(node).__name__}"
            )
        
        # Check for duplicate keys
        keys = []
        for key_node, _ in node.value:
            if isinstance(key_node, yaml.ScalarNode):
                key = self.construct_scalar(key_node)
                if key in keys:
                    raise WorkflowParseError(
                        f"Duplicate key '{key}' found at line {key_node.start_mark.line + 1}"
                    )
                keys.append(key)
        
        return super().construct_mapping(node, deep=deep)


def load_yaml(content: bytes) -> Any:
    """
    Load YAML with strict validation.
    
    Rejects:
    - Duplicate mapping keys
    - Multiple documents
    - Unsafe constructs
    
    Args:
        content: YAML content as bytes
        
    Returns:
        Parsed YAML data structure
        
    Raises:
        WorkflowParseError: if YAML is invalid
    """
    try:
        # Check for multiple documents
        documents = list(yaml.load_all(content, Loader=SafeLoaderWithDuplicateCheck))
        
        if len(documents) == 0:
            raise WorkflowParseError("Empty YAML document")
        
        if len(documents) > 1:
            raise WorkflowParseError(
                f"Multiple YAML documents found ({len(documents)}); "
                "workflow must be a single document"
            )
        
        return documents[0]
        
    except yaml.YAMLError as e:
        raise WorkflowParseError(f"YAML parsing failed: {e}") from e
