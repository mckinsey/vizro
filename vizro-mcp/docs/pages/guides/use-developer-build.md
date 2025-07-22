# How to use a developer build of Vizro-MCP

If you are a developer, or if you are running Vizro-MCP from source, you need to clone the [Vizro GitHub repository](https://github.com/mckinsey/vizro/tree/main). 

To configure the Vizro-MCP server details:

Add the following to your MCP configuration:

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

Replace `<PATH TO VIZRO>` with the actual path to the clone of the Vizro repository. 

You may also need to provide the full path to your `uv` executable, so instead of `"uv"` you would use something like `"/Users/<your-username>/.local/bin/uv"`. To discover the path of `uv` on your machine, in your terminal app, type `which uv`.
