# Implementation Guide

Deep guidance for Phase 4: Building the dashboard with MCP tools or Python.

## Contents

- MCP Setup (installation, tools reference)
- MCP Workflow (load data, validate config)
- Python Implementation (installation, basic structure, imports)
- Components Reference (Graph, AgGrid, Figure, Card, Container, Tabs)
- Controls Reference (Filter, Parameter, Button)
- Layout Reference (Grid, Flex, Nested)
- Custom Charts (@capture decorator)
- Multi-Page Dashboard
- Running the Dashboard
- Common Patterns (Overview + Detail pages)
- Number Formatting & Typography
- Grid Configuration Rules
- Documentation Links

## MCP Setup

### Checking MCP Availability

Look for `mcp__*vizro-mcp__*` tools in your available tools. If present, skip installation.

### Installing Vizro MCP

**Prerequisites**: [uv](https://docs.astral.sh/uv/getting-started/installation/) must be installed.

**For Claude Code**:

```bash
claude mcp add --transport stdio vizro-mcp -- uvx vizro-mcp
```

**Note**: The `--` separates Claude's CLI flags from the MCP server command. If `uvx` is not in PATH, use full path (find with `which uvx`).

**For Other MCP Clients** (Claude Desktop, Cursor, VS Code):

Add to your MCP settings file:

```json
{
  "mcpServers": {
    "vizro-mcp": {
      "command": "uvx",
      "args": [
        "vizro-mcp"
      ]
    }
  }
}
```

### Playwright MCP (For UI Testing)

**Claude Code**: `claude mcp add --transport stdio playwright -- npx @playwright/mcp@latest`

**Other clients**: Add `"playwright": {"command": "npx", "args": ["@playwright/mcp@latest"]}` to mcpServers.

### MCP Tools Reference

| Tool                                | Purpose                                         |
| ----------------------------------- | ----------------------------------------------- |
| `get_vizro_chart_or_dashboard_plan` | Get instructions for creating charts/dashboards |
| `get_model_json_schema`             | Get JSON schema for Vizro models                |
| `get_sample_data_info`              | Get info about built-in sample datasets         |
| `load_and_analyze_data`             | Load and analyze user's data files              |
| `validate_dashboard_config`         | Validate config and get Python code             |
| `validate_chart_code`               | Validate custom chart code                      |

## MCP Workflow

### Step 1: Load Data

```
Use: load_and_analyze_data(path_or_url="/path/to/data.csv")
```

Returns column names, types, and sample values.

### Step 2: Get Model Schemas

```
Use: get_model_json_schema(model_name="Dashboard")
Use: get_model_json_schema(model_name="Page")
Use: get_model_json_schema(model_name="Graph")
```

### Step 3: Build Configuration

Create a JSON configuration that matches Phase 1-3 decisions:

```json
{
  "pages": [
    {
      "title": "Overview",
      "components": [
        {
          "type": "graph",
          "figure": {
            "_target_": "bar",
            "data_frame": "sales",
            "x": "category",
            "y": "revenue"
          },
          "title": "Revenue by Category"
        }
      ],
      "controls": [
        {
          "type": "filter",
          "column": "region"
        }
      ]
    }
  ]
}
```

### Step 4: Validate and Get Code

```
Use: validate_dashboard_config(
  dashboard_config={...},
  data_infos=[{
    "file_name": "sales.csv",
    "file_path_or_url": "/path/to/sales.csv",
    "file_location_type": "local",
    "read_function_string": "pd.read_csv"
  }],
  custom_charts=[]
)
```

Returns Python code and optionally opens PyCafe preview.

## Python Implementation

### Installation

```bash
uv pip install vizro
# or
uv add vizro
```

### Basic Structure

```python
import pandas as pd
import vizro.models as vm
from vizro import Vizro
import vizro.plotly.express as px
from vizro.tables import dash_ag_grid

# Load data
df = pd.read_csv("data.csv")

# Create page
page = vm.Page(
    title="Dashboard",
    components=[
        vm.Graph(figure=px.bar(df, x="category", y="value"), title="Sales"),
    ],
    controls=[
        vm.Filter(column="region"),
    ],
)

# Create and run dashboard
dashboard = vm.Dashboard(pages=[page])
Vizro().build(dashboard).run()
```

### Key Imports

```python
# Core
import vizro.models as vm
from vizro import Vizro

# Charts
import vizro.plotly.express as px

# Tables
from vizro.tables import dash_ag_grid

# KPIs
from vizro.figures import kpi_card, kpi_card_reference

# Custom components
from vizro.models.types import capture

# Actions
import vizro.actions as va

# Data management
from vizro.managers import data_manager
```

## Components Reference

### Graph (Charts)

```python
vm.Graph(
    id="my_chart",  # Optional, needed for Parameter targets
    figure=px.bar(df, x="category", y="value", color="segment"),
    title="Chart Title",  # Title here, NOT in plotly
    header="Additional context",  # Optional
    footer="SOURCE: **Data source**",  # Optional, supports markdown
)
```

### AgGrid (Tables)

Always use `vm.AgGrid` with `dash_ag_grid()`:

```python
from vizro.tables import dash_ag_grid

vm.AgGrid(
    figure=dash_ag_grid(df),
    title="Data Table",
)
```

### Figure (KPIs)

```python
from vizro.figures import kpi_card, kpi_card_reference

# Simple KPI
vm.Figure(
    figure=kpi_card(
        data_frame=df,
        value_column="revenue",
        title="Total Revenue",
        value_format="${value:,.0f}",
        agg_func="sum",
        icon="payments",
    )
)

# KPI with reference comparison
vm.Figure(
    figure=kpi_card_reference(
        data_frame=df,
        value_column="revenue",
        reference_column="previous_revenue",
        title="Revenue vs Last Month",
        value_format="${value:,.0f}",
        reference_format="{delta:+.1f}%",
        reverse_color=True,  # When lower is better
    )
)
```

### Card (Text/HTML)

```python
vm.Card(
    text="""
    # Welcome
    This dashboard shows **sales performance**.
    """,
)
```

### Container

```python
vm.Container(
    title="Section Title",
    layout=vm.Grid(grid=[*[[0, 1]] * 3], row_min_height="140px"),  # 3 rows = 420px
    components=[
        vm.Graph(figure=px.bar(...)),
        vm.Graph(figure=px.line(...)),
    ],
    controls=[
        vm.Filter(column="category"),  # Scoped to this container
    ],
    variant="outlined",  # or "filled", "plain"
)
```

### Tabs

```python
vm.Tabs(
    tabs=[
        vm.Container(title="Tab 1", components=[...]),
        vm.Container(title="Tab 2", components=[...]),
    ]
)
```

## Controls Reference

### Filter

```python
# Basic filter (auto-detects selector type)
vm.Filter(column="region")

# With specific selector
vm.Filter(column="status", selector=vm.Checklist())
vm.Filter(column="date", selector=vm.DatePicker())
vm.Filter(column="price", selector=vm.RangeSlider(min=0, max=1000))
```

### Parameter

Parameters modify chart arguments (not filter data):

```python
vm.Parameter(
    targets=["chart_id.x"],  # Change x-axis column
    selector=vm.Dropdown(
        options=["revenue", "profit", "units"],
        value="revenue",
        title="Metric",
    ),
)
```

### Button with Export

```python
import vizro.actions as va

vm.Button(
    text="Export Data",
    actions=[va.export_data()],
)
```

## Layout Reference

### Grid Layout

```python
vm.Page(
    title="Dashboard",
    layout=vm.Grid(
        grid=[
            [0, 0, 1, 1, 2, 2, 3, 3],  # 4 KPIs
            [4, 4, 4, 4, 5, 5, 5, 5],  # 2 charts
            [4, 4, 4, 4, 5, 5, 5, 5],
            [4, 4, 4, 4, 5, 5, 5, 5],
            [6, 6, 6, 6, 6, 6, 6, 6],  # Full-width table
            [6, 6, 6, 6, 6, 6, 6, 6],
        ],
        row_min_height="140px",
    ),
    components=[kpi1, kpi2, kpi3, kpi4, chart1, chart2, table],
)
```

### Flex Layout

```python
vm.Page(
    title="Simple Page",
    layout=vm.Flex(),  # Automatic vertical stacking
    components=[chart1, chart2, table],
)
```

### Nested Layouts

```python
vm.Page(
    title="Mixed Layout",
    layout=vm.Flex(),
    components=[
        vm.Graph(figure=px.line(...)),
        vm.Container(
            title="Details",
            layout=vm.Grid(grid=[[0, 1, 2]]),
            components=[chart1, chart2, chart3],
        ),
    ],
)
```

## Custom Charts

Use `@capture("graph")` when you need:

- `update_layout()`, `update_xaxes()`, `update_traces()` calls
- Reference lines or annotations
- Data manipulation before visualization

```python
from vizro.models.types import capture
import vizro.plotly.express as px


@capture("graph")
def bar_with_target(data_frame, x, y, target=None):
    """Bar chart with optional horizontal target line."""
    fig = px.bar(data_frame=data_frame, x=x, y=y)
    if target is not None:
        fig.add_hline(
            y=target,
            line_dash="dash",
            line_color="red",
            annotation_text=f"Target: {target}",
        )
    return fig


# Usage
vm.Graph(
    id="sales_chart",
    figure=bar_with_target(data_frame=df, x="month", y="revenue", target=100000),
    title="Monthly Revenue vs Target",
)

# With Parameter control
vm.Parameter(
    targets=["sales_chart.target"],
    selector=vm.Slider(min=50000, max=200000, value=100000, title="Target"),
)
```

### Custom Chart Rules

1. Function must accept `data_frame` as first argument
1. Must return `plotly.graph_objects.Figure`
1. Chart titles go in `vm.Graph(title=...)`, not in the function
1. Let Vizro handle colors unless semantic coloring needed

## Multi-Page Dashboard

```python
overview = vm.Page(title="Overview", components=[...])
details = vm.Page(title="Details", components=[...])
analysis = vm.Page(title="Analysis", components=[...])

dashboard = vm.Dashboard(
    pages=[overview, details, analysis],
    navigation=vm.Navigation(nav_selector=vm.NavBar()),
)
```

## Running the Dashboard

```bash
# With uv
uv run python app.py

# Standard Python
python app.py
```

Access at `http://localhost:8050`

## Common Patterns

### Dashboard with Overview and Detail Pages

```python
# Overview page - KPIs and summary charts
overview = vm.Page(
    title="Overview",
    layout=vm.Grid(
        grid=[
            [0, 0, 1, 1],  # KPIs: 1 row = 140px
            *[[2, 2, 2, 2]] * 3,  # Chart: 3 rows = 420px
        ],
        row_min_height="140px",
    ),
    components=[
        vm.Figure(figure=kpi_card(df, "revenue", "Revenue", "${value:,.0f}")),
        vm.Figure(figure=kpi_card(df, "orders", "Orders", "{value:,}")),
        vm.Graph(figure=px.line(df, x="date", y="revenue"), title="Trend"),
    ],
    controls=[vm.Filter(column="region")],
)

# Detail page - tables and drill-downs
details = vm.Page(
    title="Details",
    layout=vm.Flex(),
    components=[
        vm.AgGrid(figure=dash_ag_grid(df), title="All Data"),
        vm.Button(text="Export", actions=[va.export_data()]),
    ],
    controls=[vm.Filter(column="region"), vm.Filter(column="product")],
)

dashboard = vm.Dashboard(pages=[overview, details])
```

## Number Formatting & Typography

### Number Formatting Rules

| Type          | Format                         | Example     |
| ------------- | ------------------------------ | ----------- |
| Large numbers | K, M, B notation               | 1.2M, 45.3K |
| Currency      | Symbol before, with separators | $1,234,567  |
| Percentages   | 1 decimal place                | 45.3%       |
| Decimals      | 0-2 places maximum             | 12.34       |
| Thousands     | Always use separators          | 1,234,567   |

**Format Strings for KPI Cards**:

```python
# Currency
value_format = "${value:,.0f}"  # $1,234,567
value_format = "${value:,.2f}"  # $1,234,567.89

# Percentages
value_format = "{value:.1f}%"  # 45.3%

# Large numbers (manual K/M/B)
value_format = "{value/1000000:.1f}M"  # 1.2M
```

### Label Best Practices

- Short and descriptive (2-5 words)
- Sentence case (not Title Case or UPPERCASE)
- No periods at end of labels
- Truncate with ellipsis if necessary (max 20 chars)

## Grid Configuration Rules

- Indices must be consecutive integers starting from 0
- Each sub-list is a row, each element is a column
- Use `*[[...]] * n` to repeat rows (makes components taller)
- Components must span rectangular areas
- Actual height = `row_min_height × rows_spanned`

## Documentation Links

- **LLM-optimized docs**: https://vizro.readthedocs.io/en/latest/llms.txt
- **User Guides**: https://vizro.readthedocs.io/en/stable/pages/user-guides/
- **API Reference**: https://vizro.readthedocs.io/en/stable/pages/API-reference/vizro/
- **Vizro MCP**: https://vizro.readthedocs.io/projects/vizro-mcp/
- **Playwright MCP**: https://github.com/microsoft/playwright-mcp
- **Claude Code MCP Guide**: https://docs.anthropic.com/en/docs/claude-code/tutorials/mcp-tutorial
