# How to use Vizro-MCP tools and templates

## Available tools (if client allows)

The Vizro-MCP server provides the following tools. In general you should not need to use them directly, but in special cases you could ask the LLM to call them directly to help it find its way.

- `get_vizro_chart_or_dashboard_plan` - Get a structured step-by-step plan for creating either a chart or dashboard. Provides guidance on the entire creation process.
- `get_model_json_schema` - Retrieves the complete JSON schema for any specified Vizro model, useful for understanding required and optional parameters.
- `validate_dashboard_config` - Tests Vizro model configurations by attempting to instantiate them. Returns Python code and visualization links for valid configurations.
- `load_and_analyze_data` - Loads a CSV file from a local path or URL into a pandas DataFrame and provides detailed analysis of its structure and content.
- `validate_chart_code` - Validates the code created for a chart and returns feedback on its correctness.
- `get_sample_data_info` - Provides information about sample datasets that can be used for testing and development.

## Available prompts (if client allows)

- `create_starter_dashboard` - Use this prompt template to get started with Vizro dashboards.
- `create_dashboard` - Use this prompt template to create a dashboard based on a local or remote CSV dataset.
- `create_vizro_chart` - Use this prompt template to create a Vizro styled plotly chart based on a local or remote CSV dataset.
