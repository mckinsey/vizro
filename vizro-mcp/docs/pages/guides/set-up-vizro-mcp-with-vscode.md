# How to set up Vizro-MCP with Visual Studio Code

!!! notice "Use of large language models"

    You must connect to a large language model (LLM) to use Vizro-MCP.

    Please review our [guidelines on the use of LLMs](../explanation/disclaimers.md).

This page explains how to set up an installation of [Visual Studio Code](https://code.visualstudio.com/) to use Vizro-MCP.

## Set up uv or Docker

To access Vizro-MCP, you must first install **either [uv](https://docs.astral.sh/uv/getting-started/installation/) or [Docker](https://www.docker.com/get-started/)** by following the linked instructions.

## Set up instructions

Once you have uv or Docker, and have installed Visual Studio Code, you need to set up the Vizro-MCP server configuration.

### Using uv

Click the "Install" button below:

[![Install with UVX in VS Code](https://img.shields.io/badge/VS_Code-Install-0098FF?style=flat-square&logo=visualstudiocode&logoColor=white)](https://insiders.vscode.dev/redirect/mcp/install?name=vizro-mcp&config=%7B%22command%22%3A%22uvx%22%2C%22args%22%3A%5B%22vizro-mcp%22%5D%7D)

### Using Docker

Click the "Install" button below:

[![Install with Docker in VS Code](https://img.shields.io/badge/VS_Code-Install-0098FF?style=flat-square&logo=visualstudiocode&logoColor=white)](https://insiders.vscode.dev/redirect/mcp/install?name=vizro-mcp&config=%7B%22command%22%3A%22docker%22%2C%22args%22%3A%5B%22run%22%2C%22-i%22%2C%22--rm%22%2C%22mcp%2Fvizro%22%5D%7D)

To use local data with Vizro-MCP, mount your data directory or directories into the container with the following extended configuration. Replace `</absolute/path/to/allowed/dir>` (syntax for folders) or `</absolute/path/to/data.csv>` (syntax for files) with the absolute path to your data on your machine. For consistency, it is recommended that the `dst` path matches the `src` path.

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
