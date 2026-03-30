---
name: writing-vizro-yaml
description: Use this skill when writing or debugging Vizro YAML dashboard configurations — component syntax, data_manager registration, custom function wiring, filter/parameter setup, or AG Grid tables. Activate when the user is building a Vizro app, encountering YAML or runtime errors, or asking about Vizro component patterns.
---

# Vizro YAML & Component Reference

## Critical Mistakes to Avoid

Each mistake below is expanded with code examples and fixes in [yaml-reference.md](references/yaml-reference.md).

1. **`@capture("graph")` receives a DataFrame** — use `data_frame` directly; never re-lookup via `data_manager[data_frame]` (causes blank charts).
1. **`data_manager` is not subscriptable** — pre-process on raw DataFrame, then register.
1. **Custom `_target_` needs module prefix** — `_target_: custom_charts.my_chart`, not `_target_: my_chart`.
1. **`type: figure` has no `title` field** — KPI titles go in `_target_: kpi_card` args.
1. **`type: ag_grid` requires `_target_: dash_ag_grid`**.
1. **Parameter targets** — format: `"component_id.argument_name"`, not `"component_id.figure"`.
1. **Quote YAML special chars in column names** — `column: "Version #"` (unquoted `#` starts a comment).
1. **Filter `targets:`** — omit when you want to apply it to all components on the page whose data source includes defined filter `column`.
1. **Grid must be rectangular** — same component index must span same columns in every row.
1. **Column type consistency** — filter column must have same dtype across all targeted datasets.

## Quick Patterns

```yaml
# Standard chart
- figure:
    _target_: bar
    data_frame: sales_data
    x: region
    y: revenue
  type: graph
  title: Revenue by Region

# KPI card (title inside figure args, NOT on component)
- figure:
    _target_: kpi_card
    data_frame: kpi_data
    value_column: Revenue
    title: Total Revenue
    value_format: "${value:,.0f}"
  type: figure

# AG Grid table
- figure:
    _target_: dash_ag_grid
    data_frame: sales_data
  type: ag_grid
  title: Sales Data

# Filter with targets
controls:
  - column: region
    targets: [chart_1, chart_2]
    type: filter
```

## Key Imports

```python
import vizro.models as vm
from vizro import Vizro
import vizro.plotly.express as px
from vizro.tables import dash_ag_grid
from vizro.figures import kpi_card, kpi_card_reference
from vizro.models.types import capture
from vizro.managers import data_manager
from vizro.themes import palettes, colors
```

## Deep Dive

Load [yaml-reference.md](references/yaml-reference.md) when you need expanded guidance. Key sections to search for:

| Need                           | Search for                   |
| ------------------------------ | ---------------------------- |
| App structure                  | `## End-to-End Data Flow`    |
| Data registration              | `## Data Registration`       |
| Custom charts                  | `## Custom Charts`           |
| AG Grid (heatmap, inline bars) | `## AG Grid Tables`          |
| Containers / Tabs              | `## Containers` or `## Tabs` |
| Expanded mistake fixes         | `## Critical Mistakes`       |
