# Vizro Chart Creator MCP Server

A simple MCP (Model Context Protocol) server that provides a prompt template for creating Vizro-compatible charts and tools for validating Vizro configurations.

## Prerequisites

- Python 3.8+
- MCP CLI (`pip install "mcp[cli]"`)
- Vizro (`pip install vizro`)

## Usage

Run the server in development mode:

```bash
mcp dev vizro_chart_server.py
```

Or install it in Claude Desktop:

```bash
mcp install vizro_chart_server.py
```

## Features

### Prompts

- `create_chart` - Generate chart code based on a dataframe and description

### Tools

- `validate_card_config` - Validate a Vizro Card configuration by attempting to instantiate it
- `get_card_schema` - Get the JSON schema for the Vizro Card model
- `get_available_models` - Get a comprehensive list of all available Vizro models organized by category

### Resources

- `schema://card` - Get the JSON schema for the Vizro Card model as a formatted string
- `models://available` - Get a formatted Markdown document listing all available Vizro models with descriptions

## Examples

### Chart Creation

When using the `create_chart` prompt, provide:
1. `data_frame`: Sample of the dataframe to use for the chart
2. `chart_description`: Description of the visualization you want to create

Example:
```python
data_frame = """
import pandas as pd
df = pd.DataFrame({
    'category': ['A', 'B', 'C', 'D'],
    'value': [10, 15, 7, 12]
})
"""
chart_description = "Create a bar chart showing values for each category with a blue color scheme"
```

The prompt will respond with Vizro-compatible chart code that follows these best practices:
- Uses plotly.express or graph_objects (not matplotlib)
- Returns a plotly figure object
- Includes appropriate titles and labels
- Handles data preprocessing within the function

### Vizro Card Validation

The `validate_card_config` tool validates Vizro Card configurations by actually instantiating them. It can accept either:
- A JSON string
- A Python dictionary directly

#### Example with JSON string:

```python
# As a JSON string (note the quotes)
await session.call_tool("validate_card_config", arguments={
    "config": """{
        "title": "My Card",
        "text": "This is a card description",
        "components": [
            {"component": "Button", "text": "Click Me"}
        ]
    }"""
})
```

#### Example with Python dictionary:

```python
# As a Python dictionary (no quotes around the object)
await session.call_tool("validate_card_config", arguments={
    "config": {
        "title": "My Card",
        "text": "This is a card description",
        "components": [
            {"component": "Button", "text": "Click Me"}
        ]
    }
})
```

#### Example responses:

Valid configuration:
```json
{
  "valid": true,
  "message": "Configuration is valid!",
  "created_object": "Card(title='My Card', text='This is a card description', ...)"
}
```

Invalid configuration:
```json
{
  "valid": false,
  "error": "Validation Error: 1 validation error for Card\ncomponents.0.action.type\n  Value error, The action type Filter is not valid [type=enum, ...]"
}
```

### Get Card Schema

You can access the Card schema in two ways:

1. **Using the tool**:
   
Call the `get_card_schema` tool to receive the complete JSON schema object.

2. **Using the resource**:

Read the `schema://card` resource to get the schema as a formatted JSON string:

```python
content, mime_type = await session.read_resource("schema://card")
print(content)
```

The schema provides detailed information about:
- Required and optional properties
- Property types
- Allowed values for enums
- Nested object structures

This helps when constructing valid Card configurations for the Vizro dashboard.

### Get Available Vizro Models

You can get a list of all available Vizro models in two ways:

1. **Using the tool**:

Call the `get_available_models` tool to get a structured dictionary of all models categorized by type:

```python
models = await session.call_tool("get_available_models")
# Access specific categories
components = models["components"]
for component in components:
    print(f"{component['name']}: {component['description']}")
```

2. **Using the resource**:

Read the `models://available` resource to get a nicely formatted Markdown document:

```python
content, mime_type = await session.read_resource("models://available")
print(content)
```

This gives you a comprehensive overview of all Vizro models available for building dashboards, organized into categories:
- Components (Button, Chart, etc.)
- Containers (Card, Page, etc.)
- Layouts (Grid, Tabs, etc.)
- Actions (Filter, Download, etc.)
- Other models

Each model includes a brief description to help you understand its purpose.

