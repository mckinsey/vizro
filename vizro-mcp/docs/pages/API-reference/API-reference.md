# API reference

# How to use Vizro-MCP tools

!!! warning

    You can use Vizro-MCP tools in Claude Desktop, but may not be allowed by other MCP hosts.

Vizro-MCP provides the following tools. In general you should not need to use them directly, but in special cases you could ask the LLM to call them directly to help it find its way.

- `get_vizro_chart_or_dashboard_plan` - Get a structured step-by-step plan for creating either a chart or dashboard. Provides guidance on the entire creation process.
- `get_model_json_schema` - Retrieves the complete JSON schema for any specified Vizro model, useful for understanding required and optional parameters.
- `validate_dashboard_config` - Tests Vizro model configurations by attempting to instantiate them. Returns Python code and visualization links for valid configurations. It opens a link to a live preview of the dashboard, which will take you to [PyCafe](https://py.cafe). If you don't want to open the link, you can tell the LLM to not do so.
- `load_and_analyze_data` - Loads a CSV file from a local path or URL into a pandas DataFrame and provides detailed analysis of its structure and content. It only uses `pd.read_xxx`, so in general there is no need to worry about privacy or data security. However, you should only run Vizro-MCP locally, not as a hosted server, because there is currently no authentication to manage access.
- `validate_chart_code` - Validates the code created for a chart and returns feedback on its correctness.
- `get_sample_data_info` - Provides information about sample datasets that can be used for testing and development.


## Reference

::: vizro_mcp
    options:
        merge_init_into_class: false
        docstring_options:
            ignore_init_summary: false
