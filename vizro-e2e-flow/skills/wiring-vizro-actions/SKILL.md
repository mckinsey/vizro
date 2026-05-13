---
name: wiring-vizro-actions
description: Use this skill when adding cross-filter, cross-highlight, drill-through, or data export interactions to a Vizro dashboard — both for choosing the right interaction pattern during design and for implementing actions in code. Activate when the user wants clicks to filter or highlight other components, needs cross-page navigation with pre-set filters, or wants users to download data.
---

# Wiring Vizro Actions

## Core concept: Source → Control → Target

All advanced interactions follow the same shape:

1. A **source** component triggers `va.set_control` when the user clicks it. Valid sources: `vm.Graph`, `vm.AgGrid`, `vm.Figure`, `vm.Button`, `vm.Card`. Graph and AgGrid carry click-data (column values from the clicked point/cell); Figure, Button, and Card pass a literal `value`.
2. `set_control` writes a value into an intermediate **control** (`vm.Filter` or `vm.Parameter`) with an explicit `id`.
3. The control updates **target** components. Filter/Parameter targets are data-bearing components: `vm.Graph`, `vm.AgGrid`, `vm.Figure`, `vm.Table`.

The control is always explicit — you do not connect components directly. This makes interactions composable (you can wire multiple sources to the same control, or one source to multiple controls).

## Built-in actions

| Action | Purpose | Trigger |
| --- | --- | --- |
| `va.export_data()` | Download all on-page data as CSV (respects filters) | `vm.Button` |
| `va.set_control(control=..., value=...)` | Set the value of a Filter or Parameter | `vm.Graph`, `vm.AgGrid`, `vm.Figure`, `vm.Button`, `vm.Card` |

`import vizro.actions as va`. Built-in actions are passed directly into `actions=` — `vm.Action` is reserved for custom `@capture("action")` functions.

```python
vm.Button(text="Export data", actions=va.export_data())
vm.Graph(actions=va.set_control(control="region_filter", value="y"))
```

## Named interaction patterns

Match data shape + user need to a pattern. Full details (when-to-use, wireframes, spec entries, code) in [actions-reference.md](references/actions-reference.md).

| # | Pattern | When to use | Key mechanic |
| --- | --- | --- | --- |
| 1 | **Hierarchical Drill-Down** (cross-page) | 2–3 level hierarchy where detail needs a dedicated page | cross-filter + `show_in_url=True` + back button + export |
| 2 | **Single-Page Drill-Down** (container) | 2-level hierarchy where detail fits in a container | cross-filter into a container |
| 3 | **Comparison Spotlight** (cross-highlight) | Compare one entity against many without removing context | custom chart with `highlight_X` + hidden Parameter |
| 4 | **Multi-Dimensional Slice** | 2+ categorical dimensions (e.g. day × time heatmap) | actions chain → multiple Filters |
| 5 | **Select & Explore** | Source chart needs to confirm selection visually AND filter targets | actions chain: self-highlight + cross-filter |
| 6 | **Data Export** | Analyst persona needs the filtered data downloaded | `vm.Button` + `va.export_data()` |

**Decision flow:**

```
Does the data have a natural hierarchy (group → individual → detail)?
├─ YES, detail needs its own page → Pattern 1
├─ YES, detail fits in a container → Pattern 2
└─ NO → continue

Compare one entity against many without removing context?
├─ YES → Pattern 3
└─ NO → continue

2+ categorical dimensions, click to drill into one cell?
├─ YES → Pattern 4
└─ NO → continue

Source chart needs visual confirmation of click AND must filter elsewhere?
├─ YES → Pattern 5
└─ NO → continue

Users need to download data?
├─ YES → Pattern 6
└─ NO → Standard filters/parameters are sufficient
```

## When NOT to use advanced interactions

- View-only dashboards (executive summary — users glance, not explore)
- Simple filtering needs (a sidebar dropdown covers it)
- Small datasets (< ~5 groups — a filter is simpler and clearer)
- More than 2 interaction patterns per page (becomes confusing)

## Key gotchas

- **`custom_data` for non-positional values**: When cross-filtering from a graph using a column that is not on a positional axis (`x`/`y`/`z`/`lat`/`lon`), add `custom_data="column"` to the figure and use `value="column"` in `set_control`. Otherwise the click does nothing.
- **`visible=False` for cross-highlight**: When a Parameter is the highlight control, hide its selector — the highlight effect itself is the feedback.
- **`"NONE"` in highlight Parameter selector options**: Include `"NONE"` as the first option so the chart starts unhighlighted.
- **`show_in_url=True` for cross-page**: Required on the target Filter. Without it, Vizro raises `ValueError` at build time and the app won't start.
- **Back button + Flex layout for drill-through targets**: Pages that receive a drill-through must use `layout=vm.Flex(direction="column")` so the back button takes natural height (Grid would waste a full 140px+ row). Put remaining content in a `vm.Container` with its own `vm.Grid`.
- **Header hint on interactive source**: Always add a short, action-oriented `header` (e.g. `header="Click a bar to filter by region"`) so users know the component is clickable.
- **Don't use `filter_interaction`**: It is deprecated. Use `va.set_control` instead.

## Quick code recipes

### Export data (Pattern 6)

```python
vm.Button(text="Export data", actions=va.export_data())
```

### Cross-filter from chart (Pattern 1 or 2)

```python
vm.Graph(
    header="Click a bar to filter by region",
    figure=px.bar("data", x="value", y="region", orientation="h"),
    actions=va.set_control(control="region_filter", value="y"),
)
vm.Filter(id="region_filter", column="region")
```

### Actions chain — one click sets multiple controls (Pattern 4 or 5)

```python
vm.Graph(
    header="Click a cell to filter the table below",
    figure=px.density_heatmap("appointments", x="day", y="time_slot"),
    actions=[
        va.set_control(control="day_filter", value="x"),
        va.set_control(control="time_filter", value="y"),
    ],
)
vm.Filter(id="day_filter", column="day", targets=["appointments_table"])
vm.Filter(id="time_filter", column="time_slot", targets=["appointments_table"])
```

### Cross-page drill-through (Pattern 1)

```python
# Source page
vm.AgGrid(
    header="Click a row to view details",
    figure=dash_ag_grid("reps"),
    actions=va.set_control(control="rep_filter", value="rep_name"),
)

# Target page
vm.Page(
    title="Rep Detail",
    layout=vm.Flex(direction="column"),
    components=[
        vm.Button(text="← Back", href="/team-overview", variant="outlined"),
        vm.Container(layout=vm.Grid(...), components=[...]),
    ],
    controls=[vm.Filter(id="rep_filter", column="rep_name", show_in_url=True)],
)
```

## Deep dive

Load [actions-reference.md](references/actions-reference.md) when you need:

| Need | Search for |
| --- | --- |
| Full pattern template (when/why/code/wireframe/spec) | `## Pattern N` |
| Positional vs `custom_data` for graph cross-filter | `## Cross-Filter from Graph` |
| Highlight-aware custom chart wiring | `## Cross-Highlight` (and see `custom_charts_guide.md` for chart shape) |
| Multi-dimensional / actions chain | `## Multi-Dimensional` or `## Actions Chains` |
| Drill-through layout constraint (Flex/Grid/back button) | `## Cross-Filter Between Pages` |
| Full common-mistakes table | `## Common Implementation Mistakes` |

## Key imports

```python
import vizro.actions as va
import vizro.models as vm
import vizro.plotly.express as px
from vizro.tables import dash_ag_grid
from vizro.models.types import capture
```
