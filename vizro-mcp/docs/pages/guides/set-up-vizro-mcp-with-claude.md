# How to set up Vizro-MCP with Claude Desktop

!!! notice "Use of large language models"

    You must connect to a large language model (LLM) to use Vizro-MCP.

    Please review our [guidelines on the use of LLMs](../explanation/disclaimers.md).

This page explains how to set up [Claude Desktop](https://support.anthropic.com/en/articles/10065433-installing-claude-desktop) to use Vizro-MCP.

!!! Warning "Can I use the free tier with Claude?"

    You do not need to have a paid account with Claude to use Vizro-MCP, but your tokens for usage will be limited. Furthermore, for best performance, we recommend using the `claude-4-sonnet` model. Using the offered `auto` setting may lead to inconsistent or unexpected results.

If you have not already done so, download and install [Claude Desktop](https://claude.ai/download). Vizro-MCP does not work with the web version of Claude.

## Set up uv or Docker

To access Vizro-MCP, you must first install **either [uv](https://docs.astral.sh/uv/getting-started/installation/) or [Docker](https://www.docker.com/get-started/)** by following the linked instructions.

## Set up instructions

Once you have uv or Docker, and have installed the desktop version of Claude, you need to set up the Vizro-MCP server configuration.

You can find `claude_desktop_config.json` through the Claude desktop UI, by navigating to the [Developer Settings](https://modelcontextprotocol.io/quickstart/user#2-add-the-filesystem-mcp-server) and choosing "Edit Config". Open the file and edit it as follows, depending on whether you're using uv or Docker.

### Using uv

If you've installed uv, open a terminal window and type `uv` to confirm that is available. To get the path to `uvx`, type the following:

```shell
which uv
```

Copy the path returned, and add the following to `claude_desktop_config.json`, substituting your path as returned above, for the placeholder given:

```
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

If you are using Docker, add the following to `claude_desktop_config.json`.

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

### Restart Claude Desktop

Once you have updated the configuration, restart Claude Desktop. After a few moments, you should see the vizro-mcp menu in the settings/context menu:

![Claude Desktop MCP Server Icon](../../assets/images/claude_working.png)
