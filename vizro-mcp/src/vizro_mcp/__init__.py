import logging
import sys

from .server import mcp

__version__ = "0.1.1"


def main():
    """Run the Vizro MCP server - makes charts and dashboards available to AI assistants."""
    # Configure logging to show warnings by default
    logging.basicConfig(level=logging.WARNING, stream=sys.stderr)

    # Run the MCP server
    mcp.run()


if __name__ == "__main__":
    main()
