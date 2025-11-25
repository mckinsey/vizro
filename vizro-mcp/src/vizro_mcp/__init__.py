"""Vizro MCP - sanitized for using without the MCP server."""

import logging
import sys

__version__ = "0.1.4.dev0"

# Core library exports - always available
from vizro_mcp._schemas import ChartPlan
from vizro_mcp._utils import DFInfo, DFMetaData
from vizro_mcp.core import (
    DataAnalysisResult,
    ModelSchemaResult,
    ValidationResult,
    get_model_schema,
    get_sample_data,
    get_vizro_version,
    load_data,
    validate_chart,
    validate_dashboard,
)

__all__ = [
    # Core validation functions
    "validate_dashboard",
    "validate_chart",
    "load_data",
    "get_model_schema",
    "get_sample_data",
    "get_vizro_version",
    # Data classes
    "ValidationResult",
    "DataAnalysisResult",
    "ModelSchemaResult",
    "DFMetaData",
    "DFInfo",
    "ChartPlan",
    # MCP server entry point
    "main",
]


def main():
    """Run the Vizro MCP server - makes charts and dashboards available to AI assistants.

    Requires the 'mcp' extra to be installed:
        pip install vizro-mcp[mcp]
    """
    try:
        from .server import mcp
    except ImportError as e:
        print(
            "Error: MCP server dependencies not installed.\n"
            "To use the MCP server, install with: pip install vizro-mcp[mcp]\n"
            f"Original error: {e}",
            file=sys.stderr,
        )
        sys.exit(1)

    # Configure logging to show warnings by default
    logging.basicConfig(level=logging.WARNING, stream=sys.stderr)

    # Run the MCP server
    mcp.run()


if __name__ == "__main__":
    main()
