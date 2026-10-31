"""CLI entry point."""

import sys
from pathlib import Path

from graph_engine import __version__
from graph_engine.api import validate_workflow_file


def main():
    """Main CLI entry point."""
    if len(sys.argv) < 2:
        print(f"Graph Engine {__version__}")
        print("Usage: pls graph <command>")
        print("Commands: validate")
        return 1
    
    command = sys.argv[1]
    
    if command == "validate":
        if len(sys.argv) < 3:
            print("Usage: pls graph validate <workflow.yaml>")
            return 1
        
        workflow_path = Path(sys.argv[2])
        report = validate_workflow_file(workflow_path)
        
        print(report.format())
        return 0 if report.is_valid else 4
    
    print(f"Unknown command: {command}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
