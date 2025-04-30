# Vizro MCP server

This page explains how to use a [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server with a LLM to create Vizro dashboards and charts.

## Without Vizro-MCP

LLMs choose any framework to create dashboards, and do so without any guidance, design principles or consistency.

❌ Random choice of frontend frameworks or charting libraries without any design principles or consistency

❌ Vibe-coded mess that may or may not run, but certainly is not very maintainable

❌ No way to easily preview the dashboard

❌ No easy way to connect to real data

## With Vizro-MCP

Vizro-MCP provides the tools and templates to create a functioning Vizro chart or dashboard step by step.

✅ One consistent framework for charts and dashboards with one common design language

✅ Validated config that is readable and easy to alter or maintain

✅ Live preview of the dashboard to iterate the design until the dashboard is perfect

✅ Use local or remote datasets simply by providing a path or URL

## 🛠️ Get started

If you are a **developer** and need instructions for running Vizro-MCP from source, skip to the end of this page to [Development or running from source](#development-or-running-from-source).

### Prerequisites

- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- [Claude Desktop](https://claude.ai/download) or [Cursor](https://www.cursor.com/downloads)

In principle, the Vizro MCP server works with _any_ MCP enabled client but we recommend Claude Desktop or Cursor as popular choices.

> 🐛 \*\* Note:\*\* There are currently some known issues with [VS Code](https://code.visualstudio.com/) but we are working on this and hope to have Copilot working soon.

> ⚠️ **Warning:** In some hosts (like Claude Desktop) the free plan might be less performant, which may cause issues when the request is too complex. In cases where the request causes the UI to crash, opt for using a paid plan, or reduce your request's complexity.

### Installation

Once you have installed the MCP host application, you need to configure the Vizro MCP server details.

**For Claud**: Add the following to your `claude_desktop_config.json` [found via Developer Settings](https://modelcontextprotocol.io/quickstart/user#2-add-the-filesystem-mcp-server).

**For Cursor**: Add the following to `mcp.json` [found via the Cursor Settings](https://docs.cursor.com/context/model-context-protocol#configuration-locations):

```json
{
  "mcpServers": {
    "git": {
      "command": "uvx",
      "args": [
        "vizro-mcp"
      ]
    }
  }
}
```

If you are using Claude Desktop, restart it, and after a few moments, you should see a hammer icon below the chat field:

<img src="assets/claud_hammer.png" alt="Claude Desktop MCP Server Icon" width="150"/>

Similarly, when using Cursor, after a short pause, you should see a green light in the MCP menu:

<img src="assets/cursor_working.png" alt="Claude Desktop MCP Server Icon" width="400"/>

> ⚠️ **Warning:** In some cases you may need to provide the full path to your `uv` executable, so instead of `uv` would use something like `/Users/<your-username>/.local/bin/uv`. To discover the path of `uv` on your machine, in your terminal app, type `which uv`.

## 💻 Usage

### Create a Vizro dashboard based on local or remote data

Example prompts:

> _Create a Vizro dashboard with one page, a scatter chart, and a filter based on `<insert absolute file path or public URL>` data._

> _Create a simple two page Vizro dashboard, with first page being a correlation analysis of `<insert absolute file path or public URL>` data, and the second page being a map plot of `<insert absolute file path or public URL>` data_

You can even ask for a dashboard without providing data:

> _Create a Vizro dashboard with one page, a scatter chart, and a filter._

In general, it helps to specify Vizro in the prompt and to keep it as precise (and simple) as possible.

### Use a prompt template to get specific dashboards quickly

We currently offer one template to create an exploratory data analysis (EDA) dashboard. This prompt template is only available in Claude Desktop. To use it, click on the plug symbol next to the hammer, and select the template.

<img src="assets/claud_hammer.png" alt="Claude Desktop MCP Server Icon" width="150"/>
<img src="assets/claude_prompt_template.png" alt="Claude Desktop MCP Server Icon" width="300"/>

### Get a live preview of your dashboard

When the LLM chooses to use the tool `validate_model_config`, and the tool executes successfully, the LLM will return a link to a live preview of the dashboard if only public data accessed via URL is used. In Claude Desktop, you can see the output of the tool by opening the tool collapsible and scrolling down to the very bottom.

<img src="assets/claude_validate.png" width="300"/>

You can also ask the model to give you the link, but it will attempt to regenerate it, which is very error prone and slow.

### Create Vizro charts

TBD

## 🔍 Transparency and trust

MCP servers are a relatively new concept, and it is important to be transparent about what the tools are capable of so you can make an informed choice as a user. Overall, the Vizro MCP server only reads data, and never writes, deletes or modifies any data on your machine.

In general the most critical part of the process is the `load_and_analyze_data` tool. This tool, running on your machine, will load local or remote data into a pandas DataFrame and provide a detailed analysis of its structure and content. It only uses `pd.read_xxx`, so in general there is no need to worry about privacy or data security.

The second most critical part is the `validate_model_config` tool. This tool will attempt to instantiate the Vizro model configuration and return the Python code and visualization link for valid configurations. If the configuration is valid, it will also return a link to a live preview of the dashboard, which will take you to [PyCafe](https://py.cafe). This of course only happens if you click the link, so you can always opt out.

## Available Tools (if client allows)

The Vizro MCP server provides the following tools. In general you should not need to use them directly, but in special cases you could ask the LLM to call them directly to help it find its way.

- `get_vizro_chart_or_dashboard_plan` - Call this tool first to get a structured step-by-step plan for creating either a chart or dashboard. Provides guidance on the entire creation process.
- `get_overview_vizro_models` - Returns a comprehensive overview of all available models in the `vizro.models` namespace, organized by category.
- `get_model_JSON_schema` - Retrieves the complete JSON schema for any specified Vizro model, useful for understanding required and optional parameters.
- `validate_model_config` - Tests Vizro model configurations by attempting to instantiate them. Returns Python code and visualization links for valid configurations.
- `load_and_analyze_csv` - Loads a CSV file from a local path or URL into a pandas DataFrame and provides detailed analysis of its structure and content.
- `get_validated_chart_code` - Validates the code created for a chart and returns feedback on its correctness.
- `get_sample_data_info` - Provides information about sample datasets that can be used for testing and development.

## Available Prompts (if client allows)

- `create_EDA_dashboard` - Use this prompt template to create an Exploratory Data Anlysis (EDA) dashboard based on a local or remote CSV dataset
- `create_vizro_chart` - Use this prompt template to create a Vizro styled plotly chart based on a local or remote CSV dataset

## Sample data

You can find a set of sample CSVs to try out in the [Plotly repository](https://github.com/plotly/datasets/tree/master).

## Development or running from source

If you are a developer, or if you are running Vizro-MCP from source, you need to clone the Vizro repo. To configure the Vizro MCP server details:

**For Claud**: Add the following to your `claude_desktop_config.json` [found via Developer Settings](https://modelcontextprotocol.io/quickstart/user#2-add-the-filesystem-mcp-server):

**For Cursor**: Add the following to `mcp.json` [found via the Cursor Settings](https://docs.cursor.com/context/model-context-protocol#configuration-locations):

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

Replace `<PATH TO VIZRO>` with the actual path to your Vizro repository. You may also need to provide the full path to your `uv` executable, so instead of `"uv"` you would use something like `"/Users/<your-username>/.local/bin/uv"`. To discover the path of `uv` on your machine, in your terminal app, type `which uv`.
