# Vizro MCP Server

A [Model Context Protocol (MCP) server](https://modelcontextprotocol.io/) to help create Vizro dashboards and charts.

## Features

- create Vizro dashboards with prompts from your IDE or Claude Desktop
- iterate the design until the dashboard is perfect
- use local or remote datasets
- take advantage of specialized prompt templates to guide dashboard creation (Claude Desktop only)

... and best of all, your result is Vizro config, so well structured, readable, (almost) guaranteed to run and no Vibe coded mess!

## Prerequisites

- [Claude Desktop](https://claude.ai/download) or [Cursor](https://www.cursor.com/downloads)
- [uv](https://docs.astral.sh/uv/getting-started/installation/)

We are working on getting [VS Code](https://code.visualstudio.com/) with Copilot working soon.

In principle, the Vizro MCP server works with _any_ MCP enabled client, the Claude Desktop and Cursor are just some of the most popular.

## Usage

Add this to your `claude_desktop_config.json` (Claude - found via Developer Settings) or `mcp.json` (Cursor - found via the Cursor Settings):

```json
"mcpServers": {
  "git": {
    "command": "uvx",
    "args": ["vizro-mcp"]
  }
}
```

## Development or running from source

For developer or if running from source, you need to clone the Vizro repo, and then add the following to your `claude_desktop_config.json` (Claude - found via Developer Settings) or `mcp.json` (Cursor - found via the Cursor Settings).

```json
{
  "mcpServers": {
    "vizro-mcp": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "<PATH TO VIZRO>/vizro-mcp/",
        "vizro-mcp"
      ]
    }
  }
}
```

Replace `<PATH TO VIZRO>` with the actual path to your Vizro repository.

## Available Tools (if client allows)

- `get_vizro_chart_or_dashboard_plan` - Call this tool first to get a structured step-by-step plan for creating either a chart or dashboard. Provides guidance on the entire creation process.
- `get_overview_vizro_models` - Returns a comprehensive overview of all available models in the `vizro.models` namespace, organized by category. 
- `get_model_JSON_schema` - Retrieves the complete JSON schema for any specified Vizro model, useful for understanding required and optional parameters.
- `validate_model_config` - Tests Vizro model configurations by attempting to instantiate them. Returns Python code and visualization links for valid configurations.
- `load_and_analyze_csv` - Loads a CSV file from a local path or URL into a pandas DataFrame and provides detailed analysis of its structure and content.
- `get_validated_chart_code` - Validates the code created for a chart and returns feedback on its correctness.

## Available Prompts (if client allows)

- `create_EDA_dashboard` - Use this prompt template to create an Exploratory Data Anlysis (EDA) dashboard based on a local or remote CSV dataset
- `create_vizro_chart` - Use this prompt template to create a Vizro styled plotly chart based on a local or remote CSV dataset

A quick way to get sample remote CSVs can be found [at the plotly repository](https://github.com/plotly/datasets/tree/master).
