# Vizro Python Quickstart

## Overview

Build Vizro dashboards using Python configuration. This guide provides basic structure, example configurations, and references to live documentation.

## Installation

```bash
uv pip install vizro # ALWAYS into a uv venv!
# or
uv add vizro
```

## Basic Structure

A Vizro app consists of:

- **Dashboard**: Main container
- **Pages**: Individual views
- **Navigation**: Automatic sidebar with page hierarchy
- **Components**: Visual elements (Graph, Table, Card, Figure)
- **Controls**: Filters and parameters
- **Actions**: User interactions (export, drill-down, cross-filtering)

## Configuration Patterns

### Example 1: Basic Page with Table and Export

From: https://vizro.readthedocs.io/en/stable/pages/tutorials/explore-components/

```python
import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.tables import dash_ag_grid
import vizro.actions as va

tips = px.data.tips()

first_page = vm.Page(
    title="Data",
    layout=vm.Flex(),
    components=[
        vm.AgGrid(
            figure=dash_ag_grid(tips, style={"height": "600px"}),
            footer="Data Source: Bryant, P. G. and Smith, M (1995)",
        ),
        vm.Button(text="Export Data", actions=va.export_data()),
    ],
)

dashboard = vm.Dashboard(pages=[first_page])
Vizro().build(dashboard).run()
```

### Example 2: Dashboard with KPIs, Charts, and Filters

From: https://vizro.readthedocs.io/en/stable/pages/tutorials/explore-components/

```python
import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.figures import kpi_card

tips = px.data.tips()

summary_page = vm.Page(
    title="Summary",
    layout=vm.Grid(grid=[[0, 1, -1, -1], [2, 2, 2, 2], [2, 2, 2, 2], [2, 2, 2, 2]]),
    components=[
        vm.Figure(
            figure=kpi_card(
                data_frame=tips,
                value_column="total_bill",
                agg_func="mean",
                value_format="${value:.2f}",
                title="Average Bill",
            )
        ),
        vm.Figure(
            figure=kpi_card(
                data_frame=tips, value_column="tip", agg_func="mean", value_format="${value:.2f}", title="Average Tips"
            )
        ),
        vm.Graph(figure=px.histogram(tips, x="total_bill")),
    ],
    controls=[
        vm.Filter(column="day"),
        vm.Filter(column="time", selector=vm.Checklist()),
        vm.Filter(column="size"),
    ],
)

dashboard = vm.Dashboard(pages=[summary_page])
Vizro().build(dashboard).run()
```

### Example 3: Custom AgGrid Table with Parameters

From: https://vizro.readthedocs.io/en/latest/pages/user-guides/custom-tables/

```python
import vizro.models as vm
import vizro.plotly.express as px
from dash_ag_grid import AgGrid
from vizro import Vizro
from vizro.models.types import capture

df = px.data.gapminder().query("year == 2007")

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
        columnDefs=[{"field": col} for col in chosen_columns],
        rowData=data_frame.to_dict("records"),
        **defaults
    )

page = vm.Page(
    title="Custom AgGrid with Parameters",
    components=[
        vm.AgGrid(
            id="custom_ag_grid",
            title="Custom Dash AgGrid",
            figure=my_custom_aggrid(
                data_frame=df,
                chosen_columns=["country", "continent", "lifeExp", "pop", "gdpPercap"]
            ),
        ),
    ],
    controls=[
        vm.Parameter(
            targets=["custom_ag_grid.chosen_columns"],
            selector=vm.Dropdown(title="Choose columns", options=df.columns.to_list()),
        )
    ],
)

dashboard = vm.Dashboard(pages=[page])
Vizro().build(dashboard).run()
```

### Example 4: Layout Configuration for Proper Spacing

**Flex Layout** (automatic spacing):
```python
import vizro.models as vm
from vizro import Vizro
import vizro.plotly.express as px
from vizro.tables import dash_ag_grid

df = px.data.iris()

page = vm.Page(
    title="Flex Layout Example",
    layout=vm.Flex(),  # Automatic spacing
    components=[
        vm.Graph(figure=px.scatter(df, x="sepal_width", y="sepal_length", color="species")),
        vm.Graph(figure=px.histogram(df, x="petal_length")),
        vm.AgGrid(figure=dash_ag_grid(df))
    ]
)

dashboard = vm.Dashboard(pages=[page])
Vizro().build(dashboard).run()
```

**Grid Layout with Row Height Control**:
```python
# Simple 2x2 grid
page = vm.Page(
    title="Grid Layout Example",
    layout=vm.Grid(
        grid=[[0, 1], [2, 2]],  # 2x2 grid, bottom row spans both columns
        row_min_height="500px"   # Prevents crowding with scroll
    ),
    components=[
        vm.Graph(figure=px.scatter(df, x="sepal_width", y="sepal_length")),  # Position 0
        vm.Graph(figure=px.histogram(df, x="petal_length")),                 # Position 1
        vm.AgGrid(figure=dash_ag_grid(df))                                   # Position 2 (spans both columns)
    ]
)
```

**Advanced Grid with Fine-Grained Control**:
```python
# Complex layout with varying row heights
page = vm.Page(
    title="Advanced Grid Layout",
    layout=vm.Grid(
        row_min_height="55px",  # Base row height
        grid=[
            [0, 0, 0, 0, 0, 0],              # Row 1: Header spans full width (6 columns)
            *[[1, 1, 1, 1, 1, 1]] * 2,       # Rows 2-3: Chart 1 full width (2 rows tall)
            *[[2, 2, 2, 2, 2, 2]] * 2,       # Rows 4-5: Chart 2 full width (2 rows tall)
            *[[3, 3, 3, 4, 4, 4]] * 5,       # Rows 6-10: Chart 3 & Table side-by-side (5 rows tall)
        ],
    ),
    components=[
        vm.Graph(figure=px.line(df, x="sepal_width", y="sepal_length")),     # 0: Header
        vm.Graph(figure=px.scatter(df, x="petal_width", y="petal_length")),  # 1: Full-width
        vm.Graph(figure=px.histogram(df, x="sepal_width")),                  # 2: Full-width
        vm.Graph(figure=px.box(df, y="petal_length")),                       # 3: Left half
        vm.AgGrid(figure=dash_ag_grid(df))                                   # 4: Right half
    ]
)
```

**Grid configuration rules**:
- Indices must be consecutive integers starting from 0
- Each sub-list is a row, each element is a column
- Use `*[[...]] * n` to repeat rows (makes components taller)
- Components must span rectangular areas
- Actual height = `row_min_height * number_of_rows_spanned`

**Nested Layouts** (Flex + Grid):
```python
page = vm.Page(
    title="Nested Layout Example",
    layout=vm.Flex(),  # Page-level: automatic flow
    components=[
        vm.Graph(figure=px.line(df, x="sepal_width", y="sepal_length")),
        vm.Container(
            title="Detailed Analysis",
            layout=vm.Grid(
                grid=[[0, 1, 2]],
                row_min_height="400px"
            ),
            components=[
                vm.Graph(figure=px.box(df, y="sepal_length")),
                vm.Graph(figure=px.box(df, y="sepal_width")),
                vm.Graph(figure=px.box(df, y="petal_length"))
            ]
        )
    ]
)
```

## Important Vizro Patterns

**Layouts**

- Use `vm.Flex()` for automatic spacing (simplest)
- Use `vm.Grid()` with `row_min_height` to control scroll behavior and prevent crowding
- Nest layouts: Flex at page level, Grid inside containers
- Reference: https://vizro.readthedocs.io/en/latest/pages/user-guides/layouts/

**Tables**

- **Always use `vm.AgGrid`** with `dash_ag_grid()` (never `go.Table`)
- For custom tables with dynamic columns, use `@capture("ag_grid")` decorator
- Reference: https://vizro.readthedocs.io/en/latest/pages/user-guides/table/

**Chart Titles and Context**

```python
# ✅ CORRECT - Title in vm.Graph
vm.Graph(
    figure=px.scatter(df, x="width", y="length", color="species"),  # No title in plotly
    title="Chart Title Here",  # Title goes in vm.Graph
    header="Additional context or methodology",  # Optional
    footer="SOURCE: **Data source**"  # Optional
)

# ❌ WRONG - Don't put title in plotly code
vm.Graph(
    figure=px.scatter(df, x="width", y="length", title="Title")  # Don't do this
)
```

**Colors**

```python
# ✅ CORRECT - Let Vizro handle colors automatically
vm.Graph(figure=px.scatter(df, x="width", y="length", color="species"))

# ❌ AVOID - Don't specify colors unless necessary for custom components
vm.Graph(figure=px.scatter(df, x="width", y="length", color_discrete_sequence=["red", "blue"]))
```

## Live Documentation

**Always reference latest docs** for current features and best practices:

- **LLM-optimized docs**: https://vizro.readthedocs.io/en/latest/llms.txt
- **User Guides**: https://vizro.readthedocs.io/en/stable/pages/user-guides/install/
- **API Reference**: https://vizro.readthedocs.io/en/stable/pages/API-reference/vizro/

## Implementation Checklist

- [ ] Install Vizro: `uv pip install vizro` or `uv add vizro` (use virtual environment if available!)
- [ ] Import required modules
- [ ] Create pages with components (Graph, Table, Card, Figure)
- [ ] Structure components in containers and tabs
- [ ] Add filters at page or container level
- [ ] Configure layout (Grid or Flex)
- [ ] Add actions (export, drill-down, cross-filtering)
- [ ] Add navigation (sidebar, page hierarchy)
- [ ] Build and run: `Vizro().build(dashboard).run()`
- [ ] Test with real data
- [ ] Review against wireframe (if available)
