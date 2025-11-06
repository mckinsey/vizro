# Vizro MCP Setup

## Overview

Vizro MCP (Model Context Protocol) provides enhanced AI assistance for building Vizro dashboards through specialized tools.

## Checking for MCP

**How to verify MCP is installed**:

- Look for `mcp__vizro-mcp__*` tools in available tools list

**If MCP available**: Skip installation and use MCP tools directly.

**If MCP not available**: Install using configuration below.

## Installation

**Prerequisites**: [uv](https://docs.astral.sh/uv/getting-started/installation/) must be installed

**MCP Configuration**:

Add to your MCP settings file (Claude Desktop, Cursor, or VS Code):

```json
{
  "mcpServers": {
    "vizro-mcp": {
      "command": "uvx",
      "args": [
        "vizro-mcp"
      ]
    }
  }
}
```

**Note**: If `uvx` is not in your PATH, use the full path (e.g., `/usr/local/bin/uvx`). Find with `which uvx`.

**Quick install links**:

- Cursor: [Install with UVX](https://cursor.com/en/install-mcp?name=vizro-mcp&config=eyJjb21tYW5kIjoidXZ4IHZpenJvLW1jcCJ9)
- VS Code: [Install with UVX](https://insiders.vscode.dev/redirect/mcp/install?name=vizro-mcp&config=%7B%22command%22%3A%22uvx%22%2C%22args%22%3A%5B%22vizro-mcp%22%5D%7D)

## Post-Installation

1. **May need to restart IDE/Claude Desktop** after adding MCP configuration
1. **Verify** MCP tools are available: Look for `mcp__vizro-mcp__*` tools
1. **Start building** with MCP assistance

## MCP Benefits

- Validation of Vizro configurations
- Data loading and analysis helpers
- Up-to-date with latest Vizro features
- AI-guided configuration generation

## Documentation

**MCP Documentation**: https://vizro.readthedocs.io/projects/vizro-mcp/
