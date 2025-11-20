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

### For Claude Code (Recommended)

Use the `claude mcp add` command to add vizro-mcp:

```bash
claude mcp add --transport stdio vizro-mcp -- uvx vizro-mcp
```

**Understanding the `--` parameter**: The `--` (double dash) separates Claude's CLI flags from the command that runs the MCP server:

- Everything **before** `--`: Claude options (like `--env`, `--scope`, `--transport`)
- Everything **after** `--`: The actual command to run (`uvx vizro-mcp`)

This prevents conflicts between Claude's flags and the server's flags.

**Note**: If `uvx` is not in your PATH, use the full path:

```bash
claude mcp add --transport stdio vizro-mcp -- /usr/local/bin/uvx vizro-mcp
```

Find the path with: `which uvx`

### For Other MCP Clients (Claude Desktop, Cursor, VS Code)

Add to your MCP settings file:

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

**Quick install links**:

- Cursor: [Install with UVX](https://cursor.com/en/install-mcp?name=vizro-mcp&config=eyJjb21tYW5kIjoidXZ4IHZpenJvLW1jcCJ9)
- VS Code: [Install with UVX](https://insiders.vscode.dev/redirect/mcp/install?name=vizro-mcp&config=%7B%22command%22%3A%22uvx%22%2C%22args%22%3A%5B%22vizro-mcp%22%5D%7D)

## Post-Installation

1. **Verify** MCP tools are available: Look for `mcp__vizro-mcp__*` tools (or `mcp__vizro__*` in some clients)
1. **Start building** with MCP assistance

## Additional MCP Server (Optional)

The vizro-e2e-flow plugin includes an additional MCP server for testing. If you installed the plugin via Claude Code, this is already configured. If setting up manually:

### Playwright MCP (For UI Testing)

**Claude Code**:

```bash
claude mcp add --transport stdio playwright -- npx @playwright/mcp@latest
```

**Other clients**: Add to MCP settings:

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": [
        "@playwright/mcp@latest"
      ]
    }
  }
}
```

## MCP Benefits

- Validation of Vizro configurations
- Data loading and analysis helpers
- Up-to-date with latest Vizro features
- AI-guided configuration generation
- Browser automation for testing (Playwright)

## Documentation

- **Vizro MCP**: https://vizro.readthedocs.io/projects/vizro-mcp/
- **Playwright MCP**: https://github.com/microsoft/playwright-mcp
- **Claude Code MCP Guide**: https://code.claude.com/docs/en/mcp
