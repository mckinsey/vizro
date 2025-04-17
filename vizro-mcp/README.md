# Vizro MCP Server

A Model Context Protocol (MCP) server that helps create Vizro dashboards and charts interactively.

## Prerequisites

- Claude Desktop
- uv

## Installation

Add the following to your Developer settings in Claude desktop
```bash
"mcpServers": {
        "vizro-mcp": {
            "command": "uv",
            "args": [
                "--directory",
                "<PATH TO VIZRO REPO>/vizro/vizro-mcp/",
                "run",
                "vizro_chart_server.py"
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
- `validated_config_to_python_code` - Convert configurations to Python code and generate PyCafe links
