# Vizro MCP Server

A Model Context Protocol (MCP) server that helps create Vizro dashboards and charts interactively.

## Prerequisites

- Claude Desktop
- uv

## Installation

You can install the package using uv:

```bash
uvx install vizro-mcp
```

## Usage

### Using the Command Line

After installation, you can run the MCP server directly:

```bash
vizro-mcp
```

### Integration with Claude Desktop

Add the following to your Developer settings in Claude desktop:

```json
"mcpServers": {
    "vizro-mcp": {
        "command": "vizro-mcp",
        "args": []
    }
}
```

Alternatively, if you're working from source:

```json
"mcpServers": {
    "vizro-mcp": {
        "command": "uv",
        "args": [
            "--directory",
            "<PATH TO VIZRO REPO>/vizro/vizro-mcp/",
            "run",
            "server.py"
        ]
    }
}
```

## Features

### Tools

- `get_vizro_chart_or_dashboard_plan` - Get a step-by-step plan for creating charts or dashboards
- `get_overview_vizro_models` - List all available Vizro models by category
- `get_model_JSON_schema` - Get the JSON schema for any Vizro model
- `validate_model_config` - Validate configurations by instantiating models
- `load_and_analyze_csv` - Load and analyze a CSV file
