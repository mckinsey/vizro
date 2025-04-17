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

If you're working from source or in a development environment, use this configuration instead:

```json
"mcpServers": {
    "vizro-mcp": {
        "command": "uv",
        "args": [
            "--directory",
            "<PATH TO VIZRO>/vizro-mcp/",
            "run",
            "vizro-mcp"
        ]
    }
}
```

Replace `<PATH TO VIZRO>` with the actual path to your Vizro repository.

## Features

### Tools

- `get_vizro_chart_or_dashboard_plan` - Call this tool first to get a structured step-by-step plan for creating either a chart or dashboard. Provides guidance on the entire creation process.
- `get_overview_vizro_models` - Returns a comprehensive overview of all available models in the vizro.models namespace, organized by category.
- `get_model_JSON_schema` - Retrieves the complete JSON schema for any specified Vizro model, useful for understanding required and optional parameters.
- `validate_model_config` - Tests Vizro model configurations by attempting to instantiate them. Returns Python code and visualization links for valid configurations.
- `load_and_analyze_csv` - Loads a CSV file from a local path or URL into a pandas DataFrame and provides detailed analysis of its structure and content.
- `get_validated_chart_code` - Validates the code created for a chart and returns feedback on its correctness.
