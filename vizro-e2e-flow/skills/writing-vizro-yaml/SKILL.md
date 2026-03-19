---
name: writing-vizro-yaml
description: Write Vizro YAML dashboard configs with correct component patterns, data_manager setup, and avoid critical implementation mistakes.
---

# Vizro YAML & Component Reference

## Critical Mistakes to Avoid

1. **`@capture("graph")` receives a DataFrame** — use `data_frame` directly; never re-lookup via `data_manager[data_frame]`.
2. **`data_manager` is not subscriptable** — pre-process on raw DataFrame, then register.
3. **Custom `_target_` needs module prefix** — `_target_: custom_charts.my_chart`, not `_target_: my_chart`.
4. **`type: figure` has no `title` field** — KPI titles go in `_target_: kpi_card` args.
5. **`type: ag_grid` requires `_target_: dash_ag_grid`**.
6. **Parameter targets** — format: `"component_id.argument_name"`, not `"component_id.figure"`.
7. **Quote YAML special chars in column names** — `column: "Version #"` (unquoted `#` starts a comment).
8. **Filter `targets:` required for pre-aggregated data** — without it, Vizro raises "column not found".
9. **Grid must be rectangular** — same component index must span same columns in every row.
10. **Column type consistency** — filter column must have same dtype across all targeted datasets.

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

Load [yaml-reference.md](references/yaml-reference.md) for: data_manager patterns, custom charts/figures/tables code, AG Grid (heatmap, inline bars), containers, tabs, navigation, and full code examples.
