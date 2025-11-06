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
