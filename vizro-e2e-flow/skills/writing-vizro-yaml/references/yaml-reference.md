# Vizro YAML & Component Reference

Shared reference for Vizro YAML syntax, component patterns, data registration, and common mistakes.

**When to read:** Implementing or converting dashboards—YAML syntax, component patterns, data registration, and critical mistakes to avoid.

## End-to-End Data Flow

```
app.py                    dashboard.yaml              custom_charts.py
──────                    ──────────────              ────────────────
1. Load raw data          Defines pages, components,  @capture("graph") functions
2. Pre-process/aggregate  layout, controls, nav       for charts needing aggregation,
3. Register in data_mgr   References data by string   parameter logic, or layout
4. Load YAML & run app    key; refs custom funcs      tweaks
```

### Minimal `app.py`

```python
from pathlib import Path
import pandas as pd
import yaml
from vizro import Vizro
from vizro.managers import data_manager
from vizro.models import Dashboard

raw = pd.read_csv("data.csv")
kpi_df = raw.groupby("region", as_index=False)["revenue"].sum()

data_manager["raw"] = raw
data_manager["kpi_data"] = kpi_df

dashboard = yaml.safe_load(Path("dashboard.yaml").read_text(encoding="utf-8"))
dashboard = Dashboard(**dashboard)

if __name__ == "__main__":
    Vizro().build(dashboard).run(port=8052)
```

## Data Registration (`data_manager`)

```python
from vizro.managers import data_manager

raw = pd.read_csv("data.csv")
pivot = raw.pivot_table(...)       # process BEFORE registering
data_manager["raw"] = raw
data_manager["pivot"] = pivot      # register the derived result
```

- `data_manager["key"]` wraps data and is **not subscriptable** — never do `data_manager["key"]["col"]`
- Do all pre-processing on the raw DataFrame variable, then register the result
- Reference by string key in YAML `data_frame:` fields

## Standard Charts (Graph)

When a chart can be expressed with Plotly Express arguments alone:

```yaml
- figure:
    _target_: bar
    data_frame: sales_data
    x: region
    y: revenue
    color: category
  type: graph
  title: Revenue by Region
```

Available standard `_target_` values: `bar`, `scatter`, `line`, `area`, `histogram`, `box`, `violin`, `strip`, `funnel`, `pie`, `treemap`, `sunburst`, `density_heatmap`, and other `px` functions.

## Custom Charts (Graph)

When a chart needs aggregation, sorting, parameter logic, or layout tweaks:

```yaml
# dashboard.yaml
- figure:
    _target_: custom_charts.metric_bar
    data_frame: raw
    metric_param: Sales
  id: metric_chart
  type: graph
```

```python
# custom_charts.py
import vizro.plotly.express as px
from vizro.models.types import capture

@capture("graph")
def metric_bar(data_frame, metric_param="Sales"):
    agg = data_frame.groupby("region", as_index=False)[metric_param].sum()
    agg = agg.sort_values(metric_param, ascending=False)
    fig = px.bar(agg, x="region", y=metric_param)
    fig.update_layout(xaxis_title=None, yaxis_title=None, legend_title=None)
    return fig
```

Key points:
- Custom functions go in `custom_charts.py` (or `custom_figures.py` / `custom_tables.py`), NOT in `app.py`
- Standard `_target_` values (like `bar`) need no module prefix; custom functions need `_target_: custom_charts.func_name`

### When to Use Custom vs Standard

| Scenario | Approach | File |
|---|---|---|
| Simple bar/line/scatter with px args | YAML `_target_: bar` | `dashboard.yaml` only |
| Chart needing aggregation before plotting | Custom function | `custom_charts.py` |
| Parameter-driven column switching | Custom function | `custom_charts.py` |
| Dual-axis charts | Custom function | `custom_charts.py` |
| Shared legend (hide on some charts) | Custom function | `custom_charts.py` |
| Heatmap table with cell coloring | Custom function | `custom_tables.py` |
| Custom KPI/figure logic | Custom function | `custom_figures.py` |

## KPI Cards

- Use built-in `kpi_card` for simple metrics, `kpi_card_reference` for comparisons
- Use `reverse_color=True` when lower is better (costs, errors)
- NEVER rebuild KPI cards as custom charts — use the built-in figures
- Only exception: when dynamically showing text as a KPI card (strictly not possible with built-in)
- Titles go inside `_target_: kpi_card` arguments, NOT on the component (`type: figure` has no `title` field)

### Built-in (no custom file needed)

```yaml
- figure:
    _target_: kpi_card
    data_frame: kpi_data
    value_column: Revenue
    title: Total Revenue
    value_format: "${value:,.0f}"
  type: figure
```

With reference comparison:

```yaml
- figure:
    _target_: kpi_card_reference
    data_frame: kpi_data
    value_column: Actual
    reference_column: Target
    title: Revenue vs Target
    value_format: "${value:,.0f}"
    reference_format: "{delta:+.1f}% vs. target"
  type: figure
```

- No `title` field on the component — title goes inside `_target_: kpi_card` arguments
- `type: figure` has **no `title` field**

### Custom KPI Card (when built-in doesn't suffice)

```yaml
# dashboard.yaml
- figure:
    _target_: custom_figures.my_kpi
    data_frame: raw_data
    value_column: id
    agg_func: count
    title: Active Resources
    value_format: "{value:,.0f}"
  type: figure
  id: kpi_count
```

```python
# custom_figures.py
import dash_bootstrap_components as dbc
import pandas as pd
from dash import html
from vizro.models.types import capture

@capture("figure")
def my_kpi(
    data_frame: pd.DataFrame,
    value_column: str,
    *,
    value_format: str = "{value}",
    agg_func: str = "sum",
    title: str | None = None,
    icon: str | None = None,
) -> dbc.Card:
    title = title or f"{agg_func} {value_column}".title()
    value = data_frame[value_column].agg(agg_func)
    header = dbc.CardHeader(
        [
            html.H4(title, className="card-kpi-title"),
            html.P(icon, className="material-symbols-outlined") if icon else None,
        ]
    )
    body = dbc.CardBody([value_format.format(value=value)])
    return dbc.Card([header, body], class_name="card-kpi")
```

- Use `@capture("figure")` (not `@capture("graph")`) for `type: figure` components
- Return `dbc.Card` with `class_name="card-kpi"` for Vizro's built-in KPI styling
- Do not use `go.Indicator` — prefer `dbc.Card`
- Round appropriately: `${value:,.0f}` not `${value:,.2f}` for large numbers
- Use `{value:.1f}%` for percentages, not excessive decimals
- Use full metric names, not abbreviations ("Conversion Rate" not "Conv Rate")
- Always include units in labels (%, $, units)
- Show comparisons where possible (vs target, vs last period)

## AG Grid Tables

### Standard Table

```yaml
- figure:
    _target_: dash_ag_grid
    data_frame: my_data
    dashGridOptions:
      pagination: true
  type: ag_grid
  title: Data Table
```

- Must use `_target_: dash_ag_grid` in the figure

### Heatmap Table (cell color encoding)

```yaml
# dashboard.yaml
- figure:
    _target_: custom_tables.heatmap_grid
    data_frame: pivot_data
  type: ag_grid
```

```python
# custom_tables.py
from vizro.tables import dash_ag_grid
from vizro.models.types import capture
from vizro.themes import palettes

_SEQ_PALETTE = palettes.sequential

def _heatmap_style_conditions(global_max):
    n = len(_SEQ_PALETTE)
    bin_size = global_max / n
    conditions = []
    for i in range(n - 1, -1, -1):
        threshold = bin_size * i
        style = {"backgroundColor": _SEQ_PALETTE[i]}
        if i >= n // 2:
            style["color"] = "white"
        conditions.append({"condition": f"params.value >= {threshold:.1f}", "style": style})
    return {"styleConditions": conditions, "defaultStyle": {}}

def _heatmap_column_defs(df, first_col_name):
    numeric_cols = df.columns[1:]
    global_max = max(df[numeric_cols].max().max(), 1)
    cell_style = _heatmap_style_conditions(global_max)

    cols = [{"field": df.columns[0], "headerName": first_col_name, "pinned": "left", "width": 130}]
    for c in numeric_cols:
        cols.append({"field": c, "headerName": str(c), "cellStyle": cell_style})
    return cols

@capture("ag_grid")
def heatmap_grid(data_frame):
    column_defs = _heatmap_column_defs(data_frame, data_frame.columns[0])
    return dash_ag_grid(data_frame=data_frame, columnDefs=column_defs)
```

- **Always use `palettes.sequential`** (or `.diverging` / `.qualitative`) — never hardcode hex/rgba colors
- **Use `styleConditions`** (not `"function"`) for conditional cell styles

### Table with Inline Bars

```yaml
# dashboard.yaml
- figure:
    _target_: custom_tables.table_with_bars
    data_frame: product_data
  type: ag_grid
  title: Product Summary
```

```python
# custom_tables.py
from vizro.models.types import capture
from vizro.tables import dash_ag_grid

@capture("ag_grid")
def table_with_bars(data_frame):
    max_count = max(int(data_frame["Count"].max()), 1)
    column_defs = [
        {"field": "Name", "flex": 2},
        {"field": "Category", "flex": 1.5},
        {
            "field": "Count",
            "width": 150,
            "cellRenderer": "BarRenderer",
            "cellRendererParams": {"maxValue": max_count},
        },
    ]
    return dash_ag_grid.__wrapped__(data_frame=data_frame, columnDefs=column_defs)
```

```javascript
// assets/dashAgGridComponentFunctions.js
var dagcomponentfuncs = (window.dashAgGridComponentFunctions =
    window.dashAgGridComponentFunctions || {});

dagcomponentfuncs.BarRenderer = function (props) {
    var maxValue =
        (props.colDef.cellRendererParams &&
            props.colDef.cellRendererParams.maxValue) || 100;
    var value = props.value || 0;
    var pct = Math.min(Math.round((value / maxValue) * 100), 100);

    return React.createElement(
        "div",
        { style: { display: "flex", alignItems: "center", gap: "6px",
                    height: "100%", padding: "4px 0" } },
        React.createElement("div", {
            style: { width: pct + "%", height: "60%",
                     backgroundColor: "var(--bs-primary)",
                     borderRadius: "2px", minWidth: value > 0 ? "4px" : "0" },
        }),
        React.createElement("span", { style: { fontSize: "0.85em" } }, value)
    );
};
```

- Place `dashAgGridComponentFunctions.js` in `assets/` (same level as `app.py`)
- **Use `dash_ag_grid.__wrapped__()`** inside custom `@capture("ag_grid")` functions to bypass the wrapper and avoid `CapturedCallable` serialization errors

## Cards (Text/Markdown)

```yaml
- text: |
    ### My Title

    Some description with **bold** and *italic* text.
  type: card
```

With header and footer:

```yaml
- text: Main card content here
  header: Card Header
  footer: Card Footer
  type: card
```

## Filters

Basic filter (auto-selects selector type):

```yaml
controls:
  - column: region
    type: filter
```

Filter with specific selector:

```yaml
controls:
  - column: region
    selector:
      type: dropdown
      title: Region
    type: filter
```

Filter targeting specific components:

```yaml
controls:
  - column: region
    targets:
      - chart_1
      - chart_2
    selector:
      type: checklist
    type: filter
```

## Parameters

```yaml
controls:
  - targets:
      - chart_id.metric_param
    selector:
      type: dropdown
      options: ["Sales", "Quantity", "Profit"]
      value: Sales
    type: parameter
```

- Target format: `"component_id.argument_name"` (NOT `"component_id.figure"`)
- Custom functions must accept the targeted argument

## Containers

```yaml
- type: container
  components:
    - figure:
        _target_: scatter
        data_frame: iris
        x: sepal_width
        y: sepal_length
      type: graph
  controls:
    - column: species
      type: filter
  variant: outlined
```

Variants: `plain`, `outlined`, `filled`.

## Tabs

```yaml
- tabs:
    - title: Tab I
      type: container
      components:
        - figure:
            _target_: bar
            data_frame: my_data
            x: category
            y: value
          type: graph
    - title: Tab II
      type: container
      components:
        - figure:
            _target_: scatter
            data_frame: my_data
            x: x_col
            y: y_col
          type: graph
  type: tabs
```

## Navigation

```yaml
navigation:
  nav_selector:
    type: nav_bar
    items:
      - label: Overview
        icon: Home
        pages:
          - Overview
      - label: Details
        icon: Info
        pages:
          - Detail Page 1
          - Detail Page 2
```

## Critical Mistakes to Avoid

### 1. `@capture("graph")` — signature and data flow

The function receives a `pd.DataFrame`, not a string. Use `data_frame` directly — do not re-lookup via `data_manager[data_frame]` (causes blank charts).

### 2. `data_manager` is not subscriptable

`data_manager["key"]` wraps data. Do all pre-processing on the raw DataFrame variable, then register the result.

### 3. `_target_` for custom functions must include module name

```yaml
# Standard — no module prefix
_target_: bar

# Custom — needs module prefix
_target_: custom_charts.my_chart
```

### 4. `type: figure` has no `title` field

KPI titles go inside the `_target_: kpi_card` arguments.

### 5. `type: ag_grid` requires `_target_: dash_ag_grid`

### 6. Parameter targets use argument names

Format: `"component_id.argument_name"`, NOT `"component_id.figure"`.

### 7. YAML `#` in column names — quote them

YAML treats `#` as a comment marker. Column names containing `#` must be quoted:

```yaml
# WRONG
- column: Version #
  type: filter

# CORRECT
- column: "Version #"
  type: filter
```

This applies to any column name containing YAML special characters (`:`, `{`, `}`, `[`, `]`, `&`, `*`, `?`, `|`, `>`, `!`, `%`, `@`, `` ` ``).

### 8. Filter targets required for pre-aggregated datasets

Filters without `targets:` apply to all components. If any component uses a dataset without the filter column, Vizro raises `"column not found"`.

### 9. Grid areas must be rectangular

See the **designing-vizro-layouts** skill for grid rectangularity rules.

### 10. Column type consistency across filter targets

A filter column must have the same data type in all targeted datasets. Convert types consistently in `app.py` before registering.

## Running the App

- Use the **latest Vizro**: in `requirements.txt` specify `vizro` only (no version pin)
- **Use unique ports per app** — `Vizro().build(dashboard).run(port=8052)` — to avoid conflicts
- Custom Python files are auto-discovered when referenced via `_target_: module.function` in YAML

## Quick Reference: Key Imports

```python
import vizro.models as vm
from vizro import Vizro
import vizro.plotly.express as px
from vizro.tables import dash_ag_grid
from vizro.figures import kpi_card, kpi_card_reference
from vizro.models.types import capture
from vizro.managers import data_manager
from vizro.themes import palettes
```
