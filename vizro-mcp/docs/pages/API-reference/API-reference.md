# API reference

The API reference serves mostly as a reference what tools are available to the model and what prompts are available to the user. The Vizro-MCP server works by allowing the LLM to call this set of carefully crafted tools. You will never call these tools directly, but this reference gives an overview over what these tools do and what the model will get as information when deciding which tool to call. Should your host not support tool calling, the usability of the MCP server is limited.

!!! note
    The `validate_dashboard_config` tool opens a link to a live preview of the dashboard, which will take you to [PyCafe](https://py.cafe). If you don't want to open the link, you can tell the LLM to not do so.

    The `load_and_analyze_data` tool loads a CSV file from a local path or URL into a pandas DataFrame and provides detailed analysis of its structure and content. It only uses `pd.read_xxx`, so in general there is no need to worry about privacy or data security. However, you should only run Vizro-MCP locally, not as a hosted server, because there is currently no authentication to manage access.


::: vizro_mcp.server
    options:
        filters:
        - "!^Data"
        - "!^Model"
        - "!^Validate"
