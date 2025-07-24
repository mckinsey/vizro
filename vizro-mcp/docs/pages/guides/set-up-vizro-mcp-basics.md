# How to set up Vizro-MCP with any MCP host

Vizro-MCP can be used with most LLM products that enable configuration of MCP server usage. For best performance, we recommend using the `claude-4-sonnet` model, or another high-performing model of your choice. Using the often-offered `auto` setting may lead to inconsistent or unexpected results.

!!! Information

    We have separate, more detailed pages, if you want to follow them to set up [Claude Desktop](./set-up-vizro-mcp-with-claude.md), [Cursor](./set-up-vizro-mcp-with-cursor.md) or [VS Code](./set-up-vizro-mcp-with-vscode.md) to use Vizro-MCP.

This page explains the basic configuration to use. In the following, we assume you have downloaded and installed the LLM app you want to configure and use as a MCP host.

## Set up uv or Docker

To access Vizro-MCP, you must first install **either [uv](https://docs.astral.sh/uv/getting-started/installation/) or [Docker](https://www.docker.com/get-started/)** by following the linked instructions.

## Set up instructions

Once you have uv or Docker, you need to set up the Vizro-MCP server configuration.

### Using uv

If you've installed uv, open a terminal window and type `uv` to confirm that is available. To get the path to `uvx`, type the following:

```shell
which uv
```

Copy the path returned, and add the following to the JSON file used to configure MCP servers for your LLM app. Be sure to substitute your path to uv as returned above, for the placeholder given:

```json
{
  "mcpServers": {
    "vizro-mcp": {
      "command": "/placeholder-path/uvx",
      "args": [
        "vizro-mcp"
      ]
    }
  }
}
```

### Using Docker

If you are using Docker, add the following to the JSON file used to configure MCP servers for your LLM app.

```json
{
  "mcpServers": {
    "vizro-mcp": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "mcp/vizro"
      ]
    }
  }
}
```

??? information "To use local data with Vizro-MCP"

    Mount your data directory or directories into the container with the following extended configuration. Replace `</absolute/path/to/allowed/dir>` (syntax for folders) or `</absolute/path/to/data.csv>` (syntax for files) with the absolute path to your data on your machine. For consistency, we recommend that the `dst` path matches the `src` path.

    ```json
    {
      "mcpServers": {
        "vizro-mcp": {
          "command": "docker",
          "args": [
            "run",
            "-i",
            "--rm",
            "--mount",
            "type=bind,src=</absolute/path/to/allowed/dir>,dst=</absolute/path/to/allowed/dir>",
            "--mount",
            "type=bind,src=</absolute/path/to/data.csv>,dst=</absolute/path/to/data.csv>",
            "mcp/vizro"
          ]
        }
      }
    }
    ```
