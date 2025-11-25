---
name: development-implementation
description: Stage 4 of Vizro dashboard development. USE AFTER completing visual-data-design. Builds the working dashboard using Vizro - connects data pipelines, implements visualizations and interactivity, creates reusable components, and ensures performance. Includes MCP setup and both MCP-based and Python implementation paths.
---

# Development & Implementation for Vizro Dashboards

## Overview

Development/Implementation transforms approved designs into functional Vizro dashboards. This stage covers the technical build process, including data integration, component development, interactivity implementation, and deployment preparation.

**Key Focus**: Build the working dashboard using Vizro. Integrate data, implement interactivity, ensure performance, and create reusable components.

## ⚠️ MANDATORY FIRST STEP: Load and Validate Specs

**STOP! Do NOT write any code until you have loaded and validated ALL specification files from previous stages.**

Use the provided specification loader script:

```bash
# Run the specification loader to validate all requirements
python scripts/load_specs.py
```

## Pre-Implementation Checklist

Before starting development, ensure you have:

- [ ] Loaded ALL specification files from stages 1-3
- [ ] Generated implementation checklist from specs
- [ ] Approved visual mockups from Stage 3
- [ ] Data source access confirmed
- [ ] Python environment with Vizro installed
- [ ] Understanding of deployment target
- [ ] Performance requirements defined

## Technology Decision Tree

```
Should I use Vizro for this dashboard?
│
├─ Python Required?
│  └─ NO → Use alternative (Tableau, Power BI, etc.)
│  └─ YES → Continue
│
├─ Check Vizro Capabilities:
│  ✓ Standard components (Graph, AgGrid, Card, Figure)
│  ✓ Filters (categorical, numerical, temporal)
│  ✓ Page-level filters in left sidebar
│  ✓ Basic actions (export, drill-down, cross-filter)
│  ✓ Multi-page navigation
│  ✓ Professional themes (light/dark)
│  ✓ Plotly Express/Graph Objects charts
│
│  ✗ CRUD operations
│  ✗ Real-time streaming
│  ✗ Complex custom workflows
│  ✗ Non-standard filter placement
│
│  Requirements fit?
│  └─ NO → Consider Dash or custom solution
│  └─ YES → Continue with Vizro
│
└─ Implementation Path:
   ├─ Option 1: MCP-based (Fastest)
   │  └─ Check for mcp__vizro__* tools
   │     └─ Available? Use MCP workflow
   │     └─ Not available? Install or use Option 2
   │
   └─ Option 2: Python-based (Manual)
      └─ Follow Python implementation guide
```

## Implementation Workflows

### Workflow A: MCP-Based Implementation (Recommended)

**Step 1: Check MCP availability**

```bash
# Check if MCP tools are available
# Look for mcp__vizro__* in tool list
```

**Step 2: Install MCP if needed**

```bash
# Install Vizro MCP server
# See references/mcp_setup.md for details
```

**Step 3: Generate dashboard with MCP**

```python
# Use MCP tools to:
# 1. Create dashboard configuration
# 2. Validate structure
# 3. Run dashboard
```

**Deliverable**: Working dashboard via MCP tools.

### Workflow B: Python Implementation (Manual)

**Step 1: Set up project structure**

```
project/
├── app.py                 # Main application
├── requirements.txt       # Dependencies
├── data/
│   └── processing.py     # Data pipeline
├── components/
│   ├── charts.py         # Reusable charts
│   └── cards.py          # KPI cards
├── assets/
│   ├── style.css         # Custom styles
│   └── logo.png          # Branding
└── config/
    └── settings.py       # Configuration
```

**Step 2: Install dependencies**

```bash
pip install vizro
# Additional: pip install gunicorn for deployment
```

**Step 3: Create basic dashboard structure**

```python
import vizro.models as vm
from vizro import Vizro
import plotly.express as px
from vizro.tables import dash_ag_grid
import pandas as pd

# Load data
df = pd.read_csv("data/sales.csv")

# Create page with components
page = vm.Page(
    title="Sales Dashboard",
    components=[
        vm.Graph(
            figure=px.line(df, x="date", y="revenue"),  # No color, no title in plotly
            title="Revenue Trend",  # Title goes in vm.Graph, not in px.line()
            header="Monthly revenue tracking for all regions",
            footer="SOURCE: **Sales database**",
        ),
        vm.AgGrid(figure=dash_ag_grid(df), title="Sales Details"),
    ],
    controls=[vm.Filter(column="region"), vm.Filter(column="product")],
)

# Create and run dashboard
dashboard = vm.Dashboard(pages=[page])
Vizro().build(dashboard).run()
```

**Important Vizro patterns**:

- **Chart titles**: Specify in `vm.Graph(title=...)`, NOT in plotly code
- **Colors**: Let Vizro handle automatically, don't specify in plotly unless necessary
- **Context**: Use `header` and `footer` parameters for additional information

**Deliverable**: Python-based Vizro dashboard.

## Core Development Tasks

### 1. Data Integration with Vizro Data Manager

Vizro uses a **Data Manager** to handle dashboard data efficiently. Choose between static or dynamic data based on your requirements.

**Quick decision guide**:

```
Need data to refresh while running?
├─ No → Use Static Data (simplest)
│   └─ Supply directly: df = pd.read_csv("data.csv")
└─ Yes → Use Dynamic Data (function)
    └─ Add to data manager with caching
```

**Static data** (simplest - data loaded once):

```python
import pandas as pd
import vizro.plotly.express as px

sales = pd.read_csv("sales.csv")
vm.Graph(figure=px.line(sales, x="date", y="revenue"))
```

**Dynamic data** (refreshable with caching):

```python
from vizro.managers import data_manager
from flask_caching import Cache

# Enable caching
data_manager.cache = Cache(config={"CACHE_TYPE": "FileSystemCache", "CACHE_DIR": "cache"})


# Define loading function
def load_sales_data():
    return pd.read_csv("sales.csv")


# Add to data manager (function, not function call!)
data_manager["sales"] = load_sales_data

# Reference by name
vm.Graph(figure=px.line("sales", x="date", y="revenue"))
```

**Key optimization tips**:

- Use static data if refresh not needed
- Enable caching for dynamic data (FileSystemCache or RedisCache in production)
- Pre-aggregate data in loading function
- Use appropriate pandas data types (`category` for strings)

**For comprehensive details**, see `references/data_manager.md`:

- Static vs dynamic data comparison
- Cache configuration and timeouts
- Parametrized data loading
- Dynamic filters
- Kedro Data Catalog integration
- Common patterns (database, API, multiple files)

**Deliverable**: Vizro data manager configuration with appropriate caching strategy.

### 2. Component Development

**Use Vizro built-in components** when possible for consistency and maintainability.

**KPI Cards with Vizro**:

```python
from vizro.figures import kpi_card, kpi_card_reference
import pandas as pd
import vizro.models as vm

# Prepare data
df = pd.DataFrame({"revenue": [1200000], "previous_revenue": [1000000]})

# Simple KPI card
revenue_kpi = vm.Figure(
    figure=kpi_card(
        data_frame=df,
        value_column="revenue",
        title="Total Revenue",
        value_format="${value:,.0f}",
        icon="trending_up",  # use icons from Google Material Icons library
    )
)

# KPI card with reference comparison (automatic color handling)
revenue_comparison = vm.Figure(
    figure=kpi_card_reference(
        data_frame=df,
        value_column="revenue",
        reference_column="previous_revenue",
        title="Revenue vs Last Month",
        value_format="${value:,.0f}",
        reference_format="{delta:+.1f}% vs previous ({reference:,.0f})",
    )
)

# For metrics where lower is better (e.g., costs, errors)
cost_kpi = vm.Figure(
    figure=kpi_card_reference(
        data_frame=df,
        value_column="costs",
        reference_column="previous_costs",
        title="Operating Costs",
        reverse_color=True,  # Green when decrease, red when increase
        value_format="${value:,.0f}",
    )
)
```

**Custom chart components** - Create advanced visuals with Vizro's `@capture("graph")` decorator:

Vizro custom charts enable advanced customization and simple data manipulation right before visualization. Use them when standard `plotly.express` charts don't provide enough control.

**When to use custom charts**:

Use the `@capture("graph")` decorator if your plotly chart needs:

- Post-update calls: `update_layout`, `update_xaxes`, `update_traces`, etc.
- Simple data manipulation: aggregation, filtering, or transformation before visualization
- Custom `plotly.graph_objects.Figure()` with manual traces via `add_trace`
- Reference lines, annotations, or custom styling not available in `plotly.express`

**Steps to create a custom chart**:

1. Define a function that returns a `go.Figure()`
1. Decorate it with `@capture("graph")`
1. Function must accept a `data_frame` argument (type: `pandas.DataFrame`)
1. All data should derive from the `data_frame` argument
1. Pass your function to the `figure` argument of `vm.Graph`

**Minimal example**:

```python
from vizro.models.types import capture
import pandas as pd
import plotly.graph_objects as go


@capture("graph")
def minimal_example(data_frame: pd.DataFrame = None):
    return go.Figure()
```

**Example 1: Enhanced scatter with reference line**

This example shows how to enhance a `plotly.express` chart with a parametrized reference line:

```python
import vizro.models as vm
import vizro.plotly.express as px
from vizro.models.types import capture


@capture("graph")
def scatter_with_line(data_frame, x, y, color=None, size=None, hline=None):
    """Scatter chart with horizontal reference line

    Args:
        data_frame: Input DataFrame (automatically filtered by Vizro)
        x, y: Column names for axes
        color, size: Optional encoding columns
        hline: Y-value for reference line (can be parametrized)
    """
    fig = px.scatter(data_frame=data_frame, x=x, y=y, color=color, size=size)
    if hline is not None:
        fig.add_hline(y=hline, line_color="gray", line_dash="dash")
    return fig


# Usage in dashboard with Parameter control
page = vm.Page(
    title="Custom Chart Example",
    components=[
        vm.Graph(
            id="enhanced_scatter",
            figure=scatter_with_line(
                data_frame=df,  # or "iris" if using data_manager
                x="sepal_length",
                y="sepal_width",
                color="species",
                size="petal_width",
                hline=3,  # Default value
            ),
            title="Sepal Dimensions",  # Title in vm.Graph, not plotly
        ),
    ],
    controls=[
        vm.Parameter(
            targets=["enhanced_scatter.hline"],
            selector=vm.Slider(min=2, max=5, step=0.5, value=3, title="Reference Line"),
        ),
    ],
)
```

**Example 2: Waterfall chart with data manipulation**

This example shows creating a custom chart type using `go.Figure()`:

```python
import pandas as pd
import plotly.graph_objects as go
from vizro.models.types import capture


@capture("graph")
def waterfall(data_frame, measure, x, y, text, title=None):
    """Custom waterfall chart with Vizro styling

    Args:
        data_frame: Input DataFrame
        measure: Column with "relative" or "total" values
        x: Category column
        y: Value column
        text: Display text column
        title: Optional chart title (prefer vm.Graph title instead)
    """
    fig = go.Figure()

    fig.add_trace(
        go.Waterfall(
            measure=data_frame[measure],
            x=data_frame[x],
            y=data_frame[y],
            text=data_frame[text],
            # Use Vizro core colors for semantic meaning
            decreasing={"marker": {"color": "#ff5267"}},  # Red for negative
            increasing={"marker": {"color": "#08bdba"}},  # Teal for positive
            totals={"marker": {"color": "#00b4ff"}},  # Blue for totals
        )
    )

    if title:
        fig.update_layout(title=title)

    return fig


# Usage
page = vm.Page(
    title="Financial Analysis",
    components=[
        vm.Graph(
            figure=waterfall(data_frame=financial_df, measure="measure", x="category", y="value", text="text"),
            title="Profit Breakdown",  # Prefer title here
        ),
    ],
    controls=[
        vm.Filter(column="category", selector=vm.Dropdown(title="Categories")),
    ],
)
```

**Example 3: Chart with data aggregation**

Use custom charts to perform simple data manipulation before visualization:

```python
@capture("graph")
def aggregated_bar(data_frame, category, value, agg_func="sum"):
    """Bar chart with built-in aggregation

    Args:
        data_frame: Input DataFrame (already filtered by Vizro)
        category: Column to group by
        value: Column to aggregate
        agg_func: Aggregation function ("sum", "mean", "count")
    """
    # Aggregate data
    if agg_func == "sum":
        agg_df = data_frame.groupby(category)[value].sum().reset_index()
    elif agg_func == "mean":
        agg_df = data_frame.groupby(category)[value].mean().reset_index()
    else:
        agg_df = data_frame.groupby(category)[value].count().reset_index()

    # Create chart with aggregated data
    fig = px.bar(agg_df, x=category, y=value)
    return fig


# Usage with Parameter to control aggregation
vm.Graph(id="agg_chart", figure=aggregated_bar(data_frame=df, category="region", value="sales", agg_func="sum"))

# Add Parameter to let users change aggregation
vm.Parameter(
    targets=["agg_chart.agg_func"],
    selector=vm.RadioItems(options=["sum", "mean", "count"], value="sum", title="Aggregation"),
)
```

**Important notes**:

- Custom charts automatically work with Filters and Parameters without extra configuration
- The `data_frame` argument receives data **after** filters and parameters are applied
- For data transformations, consider using Filters, Parameters, or data loading functions instead
- Let Vizro handle colors automatically unless you need semantic color coding
- When specifying colors, use Vizro core colors: `["#00b4ff", "#ff9222", "#3949ab", "#ff5267", "#08bdba", "#fdc935", "#689f38", "#976fd1", "#f781bf", "#52733e"]`
- Chart titles should be in `vm.Graph(title=...)`, not in plotly code
- Custom charts can be cross-filtering sources/targets like any other graph

**Reference**: https://vizro.readthedocs.io/en/stable/pages/user-guides/custom-charts/

**Component library checklist**:

- [ ] KPI cards
- [ ] Standard charts (line, bar, pie)
- [ ] AgGrid tables with sorting/filtering
- [ ] Filters and controls
- [ ] Custom layouts

**Table best practices**:

- **Always use `vm.AgGrid`** with `dash_ag_grid()` for tables (not `vm.Table` or `go.Table`)
- AgGrid provides sorting, filtering, pagination, and better UX
- For custom tables with dynamic columns or advanced features, use `@capture("ag_grid")` decorator:

```python
from dash_ag_grid import AgGrid
from vizro.models.types import capture


@capture("ag_grid")
def my_custom_aggrid(chosen_columns: list[str], data_frame=None):
    defaults = {
        "className": "ag-theme-quartz-dark ag-theme-vizro",
        "defaultColDef": {
            "resizable": True,
            "sortable": True,
            "filter": True,
            "filterParams": {"buttons": ["apply", "reset"], "closeOnApply": True},
            "flex": 1,
            "minWidth": 70,
        },
    }
    return AgGrid(
        columnDefs=[{"field": col} for col in chosen_columns], rowData=data_frame.to_dict("records"), **defaults
    )


# Use with Parameter to allow column selection
vm.AgGrid(id="custom_ag_grid", figure=my_custom_aggrid(data_frame=df, chosen_columns=["col1", "col2"]))
```

- Reference: https://vizro.readthedocs.io/en/latest/pages/user-guides/table/

**Color best practices**:

- **Standard charts**: Do NOT specify colors - let Vizro apply theme colors automatically
- **Custom components**: Use Vizro core colors when needed:
    - Pick 2-3 from: `["#00b4ff", "#ff9222", "#3949ab", "#ff5267", "#08bdba", "#fdc935", "#689f38", "#976fd1", "#f781bf", "#52733e"]`
    - Use `"gray"` for neutral elements
    - Success/positive: `"#689f38"`, Warning: `"#ff9222"`, Error/negative: `"#ff5267"`

**Using Containers to organize components**:

Containers group related components into sections with optional titles, filters, and styling:

```python
import vizro.models as vm

page = vm.Page(
    title="Analytics Dashboard",
    components=[
        # Top-level KPIs (no container)
        vm.Graph(figure=revenue_kpi),
        vm.Graph(figure=orders_kpi),
        # Container 1: Sales Analysis
        vm.Container(
            title="Sales Analysis",
            components=[
                vm.Graph(figure=sales_chart),
                vm.Graph(figure=regional_breakdown),
            ],
            controls=[
                vm.Filter(column="region"),  # Affects only this container
            ],
            variant="filled",
        ),
        # Container 2: Customer Metrics
        vm.Container(
            title="Customer Metrics",
            components=[
                vm.Graph(figure=customer_chart),
                vm.AgGrid(figure=customer_table),
            ],
            controls=[
                vm.Filter(column="segment"),  # Affects only this container
            ],
            variant="outlined",
        ),
    ],
    controls=[
        vm.Filter(column="date"),  # Page-level filter (affects all components)
    ],
)
```

**When to use containers**:

- Group related components into logical sections
- Add section titles for clarity
- Apply filters/parameters to specific sections only
- Create visual separation with custom layouts or styling
- Control spacing differently for each section

**Container controls**: Filters and parameters inside containers affect only that container's components (not the whole page).

**Reference**: https://vizro.readthedocs.io/en/stable/pages/user-guides/container/

**Deliverable**: Reusable component library.

### 3. Implement Interactivity

**Cross-filtering implementation**:

```python
# Using Vizro actions
import vizro.models as vm

page = vm.Page(
    title="Interactive Dashboard",
    components=[
        vm.Graph(id="chart-1", ...),
        vm.Graph(id="chart-2", ...),
    ],
    actions=[
        vm.Action(
            function="filter_interaction",
            inputs=["chart-1.clickData"],
            outputs=["chart-2.figure"]
        )
    ]
)
```

**Interaction types to implement**:

- [ ] Hover tooltips
- [ ] Click to filter
- [ ] Drill-down navigation
- [ ] Export functionality
- [ ] Parameter controls

**Deliverable**: Interactive features implementation.

### 4. Configure Layout for Proper Spacing

**Two approaches to prevent crowded components**:

**Option 1: Flex Layout** (automatic spacing)

```python
page = vm.Page(
    title="Dashboard",
    layout=vm.Flex(),  # Automatically adds spacing between components
    components=[vm.Graph(figure=chart1), vm.Graph(figure=chart2), vm.AgGrid(figure=table)],
)
```

**Option 2: Grid Layout with Row Height Control** (fine-grained control)

Grid layout provides precise control over component arrangement. Each component is assigned an index (0, 1, 2...) and positioned in the grid.

**Basic grid configuration**:

```python
page = vm.Page(
    title="Dashboard",
    layout=vm.Grid(
        grid=[[0, 1], [0, 2]],  # Component 0 spans 2 rows, 1 and 2 in separate cells
        row_min_height="500px",  # Ensures sufficient height per row
    ),
    components=[
        vm.Graph(figure=chart1),  # Position 0 (left column, spans rows 1-2)
        vm.Graph(figure=chart2),  # Position 1 (top-right)
        vm.AgGrid(figure=table),  # Position 2 (bottom-right)
    ],
)
```

**Grid configuration rules**:

- Grid provided as `list[list[int]]` (e.g., `[[0, 1], [0, 2]]`)
- Integers must be consecutive starting from 0
- Integers correspond to component index in the components list
- Each sub-list = one grid row
- Each element in sub-list = one grid column
- Components span rectangular areas only
- Can use arbitrarily large grids for granular control

**Advanced grid with varying row heights**:

```python
page = vm.Page(
    title="Complex Dashboard",
    layout=vm.Grid(
        row_min_height="55px",  # Base row height
        grid=[
            [0, 0, 0, 0, 0, 0],  # Row 1: Component 0 spans full width
            *[[1, 1, 1, 1, 1, 1]] * 2,  # Rows 2-3: Component 1 (2 rows tall)
            *[[2, 2, 2, 2, 2, 2]] * 2,  # Rows 4-5: Component 2 (2 rows tall)
            *[[3, 3, 3, 4, 4, 4]] * 5,  # Rows 6-10: Components 3 & 4 side-by-side (5 rows tall)
        ],
    ),
    components=[
        vm.Graph(figure=header_chart),  # 0: Full-width header (1 row)
        vm.Graph(figure=chart1),  # 1: Full-width chart (2 rows)
        vm.Graph(figure=chart2),  # 2: Full-width chart (2 rows)
        vm.Graph(figure=chart3),  # 3: Left half (5 rows)
        vm.AgGrid(figure=table),  # 4: Right half (5 rows)
    ],
)
```

**Grid layout tips**:

- Use `*[[...]] * n` to repeat rows for taller components
- Base `row_min_height` is multiplied by number of rows a component spans
- Larger grids (e.g., 6 columns vs 2) provide finer positioning control
- Components automatically span their entire grid area
- Use empty cells (by using -1) to create spacing

**Nested Layouts** (Flex at page level, Grid inside containers):

```python
page = vm.Page(
    title="Dashboard",
    layout=vm.Flex(),  # Page-level: automatic flow
    components=[
        vm.Graph(figure=header_chart),
        vm.Container(
            title="Analysis Section",
            layout=vm.Grid(
                grid=[[0, 1, 2], [3, 3, 3]],  # Structured grid inside container
                row_min_height="400px",
            ),
            components=[
                vm.Graph(figure=chart1),
                vm.Graph(figure=chart2),
                vm.Graph(figure=chart3),
                vm.AgGrid(figure=table),
            ],
        ),
    ],
)
```

**Layout best practices**:

- Use `vm.Flex()` for simple pages with automatic spacing
- Use `vm.Grid()` with `row_min_height` for precise control and scroll behavior
- For fine-grained control: Use larger grids (6-12 columns) with varying row heights
- Nest layouts: Flex at page level, Grid inside containers for structured sections
- Set `row_min_height` so components inside grid can take enough space for proper rendering
- Component actual height = `row_min_height * rows_spanned`
- Reference: https://vizro.readthedocs.io/en/latest/pages/user-guides/layouts/

**Deliverable**: Page layouts with proper component spacing.

## Deployment Preparation

### Local Development

```bash
# Development server
uv run python app.py
# Access at http://localhost:8050
```

## REQUIRED OUTPUT: spec/4_implementation_report.yaml

After completing implementation, create a report documenting what was built:

```yaml
# spec/4_implementation_report.yaml
spec_compliance:
  followed_specs: boolean
  deviations: list[string]  # Any necessary changes from specs

implementation_complete: boolean
```

## Deliverables Checklist

### Required Outputs

1. **Source Code**

    - Main application file
    - Data processing modules
    - Component library
    - Configuration files

1. **Specification Compliance**

    - spec/4_implementation_checklist.yaml
    - spec/4_implementation_report.yaml
    - Validation log showing all checks passed

1. **Documentation**

    - README with setup instructions
    - API documentation
    - Configuration guide
    - Deployment instructions

## Common Implementation Patterns

### Multi-Page Navigation

```python
dashboard = vm.Dashboard(
    pages=[
        vm.Page(title="Overview", ...),
        vm.Page(title="Details", ...),
        vm.Page(title="Analysis", ...)
    ],
    navigation=vm.Navigation(
        nav_selector=vm.NavBar()  # or vm.NavPanel()
    )
)
```

## Validation Checklist

Before proceeding to Test & Iterate:

- [ ] All pages implemented per design
- [ ] Documentation complete

## Next Steps

Once Development is complete, proceed to **test-iterate** skill for validation

## Troubleshooting Guide

### Common Issues and Solutions

| Issue              | Cause                | Solution                                                           |
| ------------------ | -------------------- | ------------------------------------------------------------------ |
| Slow initial load  | Large datasets       | Implement pagination and avoid expensive charts like scatter chart |
| Filter not working | Column type mismatch | Ensure correct data types                                          |
| Style not applied  | CSS specificity      | Use !important or increase specificity                             |

## Resources

- Vizro Documentation: https://vizro.readthedocs.io/
- Vizro Examples: https://vizro.readthedocs.io/en/stable/pages/examples/
- Plotly Documentation: https://plotly.com/python/
