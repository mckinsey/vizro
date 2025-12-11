---
name: development-implementation
description: Stage 4 of Vizro dashboard development. USE AFTER completing visual-data-design. Builds the working dashboard using Vizro - connects data pipelines, implements visualizations and interactivity, creates reusable components, and ensures performance. Includes MCP setup and both MCP-based and Python implementation paths.
---

# Development & Implementation for Vizro Dashboards

**Key Focus**: Build the working dashboard. Integrate data, implement interactivity, create reusable components.

**⚠️ IMPORTANT**: This is an EXECUTION stage. Implement spec files exactly - do not redesign.

## Contract Files (MUST READ FIRST)

| File                                   | Contains                      |
| -------------------------------------- | ----------------------------- |
| `spec/1_information_architecture.yaml` | Pages, KPIs, data structure   |
| `spec/2_interaction_ux.yaml`           | Filters, controls, navigation |
| `spec/3_visual_design.yaml`            | Chart types, colors, styling  |

## Getting Started

- See `references/python_quickstart.md` for complete setup and code examples
- See `references/mcp_setup.md` for MCP server setup

## Implementation Workflow

**IMPORTANT: Use Vizro MCP tools to build dashboards**

**Step 1: Check MCP availability**

Verify MCP tools are available by looking for `mcp__plugin_vizro-e2e-flow_vizro-mcp__*` tools in your tool list.

**Step 2: Install MCP if needed**

If MCP tools aren't available, see `references/mcp_setup.md` for installation instructions.

**Step 3: Use MCP to generate dashboard**

Use the MCP tools to:

1. Load and analyze your data with `load_and_analyze_data`
1. Get the JSON schema for the specified Vizro model with `get_model_json_schema`
1. Create dashboard configuration (IMPORTANT: strictly respect `spec/` files from stages 1-3) and validate configuration with `validate_dashboard_config`
1. Get Python code from validated output

The MCP workflow ensures your implementation matches the approved specs and follows Vizro best practices.

## Basic Dashboard Structure (for reference)

```python
import vizro.models as vm
from vizro import Vizro
import vizro.plotly.express as px
from vizro.tables import dash_ag_grid

df = pd.read_csv("data/sales.csv")

page = vm.Page(
    title="Sales Dashboard",
    components=[
        vm.Graph(
            figure=px.line(df, x="date", y="revenue"),
            title="Revenue Trend",  # Title in vm.Graph, not plotly
        ),
        vm.AgGrid(figure=dash_ag_grid(df), title="Sales Details"),
    ],
    controls=[vm.Filter(column="region"), vm.Filter(column="product")],
)

dashboard = vm.Dashboard(pages=[page])
Vizro().build(dashboard).run()
```

## Data Integration

**Static data** (simplest - loaded once):

```python
sales = pd.read_csv("sales.csv")
vm.Graph(figure=px.line(sales, x="date", y="revenue"))
```

**Dynamic data** (refreshable with caching):

```python
from vizro.managers import data_manager
from flask_caching import Cache

data_manager.cache = Cache(config={"CACHE_TYPE": "FileSystemCache", "CACHE_DIR": "cache"})


def load_sales_data():
    return pd.read_csv("sales.csv")


data_manager["sales"] = load_sales_data  # Function, not call!
vm.Graph(figure=px.line("sales", x="date", y="revenue"))  # Reference by name
```

See `references/data_manager.md` for cache configuration and advanced patterns.

## KPI Cards

```python
from vizro.figures import kpi_card, kpi_card_reference

# Simple KPI
vm.Figure(
    figure=kpi_card(
        data_frame=df,
        value_column="revenue",
        title="Total Revenue",
        value_format="${value:,.0f}",
        icon="trending_up",
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
        reverse_color=True,  # Use when lower is better
    )
)
```

## Custom Charts

Use `@capture("graph")` for charts needing `update_layout`, reference lines, or data manipulation:

```python
from vizro.models.types import capture
import vizro.plotly.express as px


@capture("graph")
def scatter_with_line(data_frame, x, y, color=None, hline=None):
    fig = px.scatter(data_frame=data_frame, x=x, y=y, color=color)
    if hline is not None:
        fig.add_hline(y=hline, line_color="gray", line_dash="dash")
    return fig


# Usage with Parameter control
vm.Graph(
    id="chart",
    figure=scatter_with_line(data_frame=df, x="x", y="y", hline=3),
    title="Chart Title",
)
vm.Parameter(
    targets=["chart.hline"],
    selector=vm.Slider(min=0, max=10, value=3, title="Reference Line"),
)
```

**Key rules**:

- Function must accept `data_frame` argument
- Must return `go.Figure()`
- Chart titles in `vm.Graph(title=...)`, not plotly
- Let Vizro handle colors unless semantic coloring needed

## Tables

Always use `vm.AgGrid` with `dash_ag_grid()`:

```python
from vizro.tables import dash_ag_grid

vm.AgGrid(figure=dash_ag_grid(df), title="Data Table")
```

## Containers

Group components with scoped filters:

```python
vm.Container(
    title="Sales Analysis",
    components=[vm.Graph(figure=chart1), vm.Graph(figure=chart2)],
    controls=[vm.Filter(column="region")],  # Affects only this container
    variant="outlined",  # or "filled", "plain"
)
```

## Layouts

**Optimal Grid Strategy** (recommended):

Use **8 or 12 columns** with `row_min_height="140px"`

```python
# 8-column grid (recommended for most dashboards)
vm.Page(
    title="Dashboard",
    layout=vm.Grid(
        grid=[
            [0, 0, 1, 1, 2, 2, 3, 3],  # Row 1: 4 KPI cards (2 cols each)
            [4, 4, 6, 6, 6, 7, 7, 7],  # Row 2-4: 2 KPIs + 2 charts
            [5, 5, 6, 6, 6, 7, 7, 7],  # Charts are 3 cols × 3 rows
            [-1, -1, 6, 6, 6, 7, 7, 7],  # Use -1 for spacing
            [8, 8, 8, 8, 8, 8, 8, 8],  # Rows 5-8: Full-width table
            [8, 8, 8, 8, 8, 8, 8, 8],
            [8, 8, 8, 8, 8, 8, 8, 8],
            [8, 8, 8, 8, 8, 8, 8, 8],
        ],
        row_min_height="140px",
    ),
    components=[kpi1, kpi2, kpi3, kpi4, kpi5, kpi6, chart1, chart2, table],
)

# 12-column grid (for more complex layouts)
vm.Page(
    title="Dashboard",
    layout=vm.Grid(
        grid=[
            [0, 0, 0, 1, 1, 1, 2, 2, 2, 3, 3, 3],  # 4 KPI cards (3 cols each)
            [4, 4, 4, 4, 5, 5, 5, 5, 6, 6, 6, 6],  # 3 charts side-by-side (4 cols each)
            [4, 4, 4, 4, 5, 5, 5, 5, 6, 6, 6, 6],
            [4, 4, 4, 4, 5, 5, 5, 5, 6, 6, 6, 6],
        ],
        row_min_height="140px",
    ),
    components=[kpi1, kpi2, kpi3, kpi4, chart1, chart2, chart3],
)
```

**Component sizing guidelines**:

- **KPI cards**: 2-3 columns × 1 row (140px)
- **Charts**: minimum 3-4 columns × 3 rows (420px)
- **Tables**: full width, adjust rows as needed
- **Empty cells**: use `-1` for spacing

**Grid rules**:

- Use 8 columns for standard layouts, 12 columns for finer control
- Indices must be consecutive from 0 (skip -1)
- Each sub-list = one row
- Component height = `row_min_height × rows_spanned`

## Multi-Page Navigation

```python
dashboard = vm.Dashboard(
    pages=[
        vm.Page(title="Overview", ...),
        vm.Page(title="Details", ...),
    ],
    navigation=vm.Navigation(nav_selector=vm.NavBar())
)
```

## REQUIRED OUTPUT: spec/4_implementation_report.yaml

```yaml
spec_compliance:
  followed_specs: boolean
  deviations: list[string]
implementation_complete: boolean
```

## Run Dashboard

```bash
uv run python app.py
# Access at http://localhost:8050
```

## Next Step

Proceed to **test-iterate** skill.
