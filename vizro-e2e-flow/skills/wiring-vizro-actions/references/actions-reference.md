# Vizro Actions Reference

Full reference for the **wiring-vizro-actions** skill. Each named pattern below covers both design-phase decisions (when to use, wireframe, spec entry) and build-phase implementation (full code). The cross-cutting "Action Mechanics" section near the bottom is a quick-reference for code patterns shared across patterns.

## Contents

- Core Concept (Source → Control → Target)
- Pattern 1: Hierarchical Drill-Down (cross-page)
- Pattern 2: Single-Page Drill-Down (container)
- Pattern 3: Comparison Spotlight (cross-highlight)
- Pattern 4: Multi-Dimensional Slice
- Pattern 5: Select & Explore (self-highlight + cross-filter)
- Pattern 6: Data Export
- Action Mechanics Reference
  - Export Data
  - Cross-Filter from Table
  - Cross-Filter from Graph (positional vs `custom_data`)
  - Cross-Highlight wiring
  - Cross-Filter Between Containers
  - Cross-Filter Between Pages
  - Multi-Dimensional Cross-Filter
  - Actions Chains
- Visual Affordances
- Common Implementation Mistakes

## Core Concept

All advanced interactions follow **Source → Control → Target**:

```
[Source]                [Control]                  [Target(s)]
 Graph                   Filter (id=...)            Graph
 AgGrid    --click-->    or Parameter      ---->    AgGrid
                         (visible=True/False)       Figure
          va.set_control(control=..., value=...)
```

- The control is **always explicit** with an `id`. You never connect source to target directly.
- The source uses `va.set_control` (a built-in action). The control then drives the target.
- Targets are inferred from the control: a Filter's `targets` (or its container scope), a Parameter's `targets`.
- This shape composes: multiple sources can write to the same control; one source can chain multiple `set_control` calls.

## Pattern 1: Hierarchical Drill-Down (cross-page)

**Domain example**: Sales Pipeline (Region → Sales Rep → Deals).

### When to use

- 2–3 level hierarchy (region → rep → deals, department → employee → tasks).
- Users start broad, narrow by group, then deep-dive into individual records.
- The detail level has enough content to justify its own page.

### When NOT to use

- Only 1 level (use Pattern 2 or standard filters).
- Fewer than ~5 top-level groups (a sidebar dropdown filter is simpler).
- Detail fits comfortably in a container — then use Pattern 2.

### Interaction flow

```
Page 1 (Overview) ──click rep row──> sets rep_filter (show_in_url=True)
                                              │
                                              ▼
                                       Page 2 (Detail), filtered to that rep
                                              │
                                              └──> [← Back] returns to Page 1
                                              └──> [Export] downloads filtered data
```

### Wireframe — Page 1: Overview

```
+--+----------+------------------------------------------------------------------------+
|  |NAV       |                                                                        |
|  |Overview ●|  +-----------+  +-----------+  +-----------+  +-----------+             |
|  |Detail    |  | KPI 1     |  | KPI 2     |  | KPI 3     |  | KPI 4     |             |
|  |----------|  +-----------+  +-----------+  +-----------+  +-----------+             |
|  |FILTERS   |                                                                        |
|  |Quarter   |  +----------------------------------+  +-----------------------------+  |
|  |[v]       |  |  CHART: Pipeline by Region       |  |  CHART: Win Rate Trend       |  |
|  |          |  |  header: "Click a bar to filter" |  |  [Line chart]                |  |
|  |Stage     |  |  [Horizontal Bar]                |  |                              |  |
|  |[v]       |  |  [click: cross-filter → region]  |  |                              |  |
|  |          |  +----------------------------------+  +-----------------------------+  |
|  |          |                                                                        |
|  |          |  CONTAINER: Rep Breakdown [filtered by region]                          |
|  |          |  +----------------------------------+  +-----------------------------+  |
|  |          |  |  CHART: Rep Pipeline             |  |  CHART: Rep vs Target        |  |
|  |          |  +----------------------------------+  +-----------------------------+  |
|  |          |  +----------------------------------------------------------------+    |
|  |          |  |  TABLE: Sales Reps                                              |    |
|  |          |  |  header: "Click a row to view details"                          |    |
|  |          |  |  [click: drill-through → rep_filter → Detail page]              |    |
|  |          |  +----------------------------------------------------------------+    |
+--+----------+------------------------------------------------------------------------+
```

### Wireframe — Page 2: Detail (Flex layout)

```
+--+----------+------------------------------------------------------------------------+
|  |NAV       |                                                                        |
|  |Overview  |  [← Back]  (Button, variant=outlined, href=/overview)                    |
|  |Detail   ●|                                                                        |
|  |----------|  CONTAINER: Detail Content (Grid layout)                                |
|  |FILTERS   |  +-----------+  +-----------+  +-----------+  +-----------+             |
|  |Rep Name  |  | KPI 1     |  | KPI 2     |  | KPI 3     |  | KPI 4     |             |
|  |[v]       |  +-----------+  +-----------+  +-----------+  +-----------+             |
|  |          |  +----------------------------------+  +-----------------------------+  |
|  |          |  |  CHART: Pipeline by Stage        |  |  CHART: Deal Timeline        |  |
|  |          |  +----------------------------------+  +-----------------------------+  |
|  |          |  +----------------------------------------------------------------+    |
|  |          |  |  TABLE: All Deals (sortable, full record detail)                |    |
|  |          |  +----------------------------------------------------------------+    |
|  |          |                                                                        |
|  |          |  [BUTTON: Export data]                                                 |
+--+----------+------------------------------------------------------------------------+
```

### Spec entry

```yaml
# spec/2_interaction_ux.yaml — interactions section
interactions:
  - type: cross-filter
    pattern: Hierarchical Drill-Down
    trigger: click bar in "Pipeline by Region"
    source: Pipeline by Region (Graph)
    source_value: "y"              # region on y-axis (horizontal bar)
    control_id: region_filter
    control_type: filter
    control_column: region
    targets: all components in "Rep Breakdown" container
    placement: container-level
    visible: true

  - type: cross-page-drill-through
    pattern: Hierarchical Drill-Down
    trigger: click row in "Sales Reps" table
    source: Sales Reps (AgGrid)
    source_value: "rep_name"
    control_id: rep_filter
    control_type: filter
    control_column: rep_name
    targets: all components on "Rep Detail" page
    placement: page-level (Rep Detail)
    visible: true
    show_in_url: true

  - type: export_data
    pattern: Hierarchical Drill-Down
    trigger: click "Export data" button
    page: Rep Detail
```

### Code (cross-page drill-through with back button)

```python
import vizro.actions as va
import vizro.models as vm
import vizro.plotly.express as px
from vizro.tables import dash_ag_grid

# Page 1: Overview
page_overview = vm.Page(
    title="Pipeline Overview",
    components=[
        vm.Graph(
            id="pipeline_by_region",
            header="Click a bar to filter by region",
            figure=px.bar("pipeline", x="pipeline_value", y="region", orientation="h"),
            actions=va.set_control(control="region_filter", value="y"),
        ),
        vm.Container(
            title="Rep Breakdown",
            variant="filled",
            components=[
                vm.Graph(id="rep_pipeline", figure=px.bar("reps", x="pipeline", y="rep", orientation="h")),
                vm.AgGrid(
                    id="reps_table",
                    header="Click a row to view rep details",
                    figure=dash_ag_grid("reps"),
                    actions=va.set_control(control="rep_filter", value="rep_name"),
                ),
            ],
            controls=[vm.Filter(id="region_filter", column="region")],  # scoped to container
        ),
    ],
)

# Page 2: Detail
page_detail = vm.Page(
    title="Rep Detail",
    layout=vm.Flex(direction="column"),  # REQUIRED for back button
    components=[
        vm.Button(text="← Back", href="/pipeline-overview", variant="outlined"),
        vm.Container(
            layout=vm.Grid(grid=[[0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2]]),
            components=[
                vm.Graph(id="stage_chart", figure=px.bar("deals", x="value", y="stage", orientation="h")),
                vm.Graph(id="timeline", figure=px.line("deals", x="date", y="value")),
                vm.AgGrid(id="deals_table", figure=dash_ag_grid("deals")),
            ],
        ),
        vm.Button(text="Export data", actions=va.export_data()),
    ],
    controls=[vm.Filter(id="rep_filter", column="rep_name", show_in_url=True)],
)
```

### Key decisions

| Decision | Choice | Reasoning |
| --- | --- | --- |
| Region filter visible | Yes | User can switch regions manually without re-clicking the chart |
| Rep filter visible on Page 2 | Yes | User can browse other reps without going back |
| `show_in_url=True` on `rep_filter` | Required | Cross-page drill-through; also lets users bookmark/share |
| Horizontal bars | Always | Prevents crowded labels; `value="y"` for cross-filter |
| Page 2 Flex layout | Required | Back button needs natural height (Grid would waste a row) |
| Header hint on source | Required | User must know the component is clickable |
| Export on Page 2 only | Intentional | Detail page is where users export filtered data |

---

## Pattern 2: Single-Page Drill-Down (container)

**Domain example**: HR Dashboard (Department → Employee metrics).

### When to use

- 2-level hierarchy where the detail fits in a container on the same page.
- Users want to drill in without leaving the page.
- Simpler than Pattern 1 — no cross-page navigation, no back button.

### When NOT to use

- Detail content is too large for a container (use Pattern 1).
- Only 1 level (standard filter suffices).

### Interaction flow

```
[Bar chart in main area] ──click bar──> sets dept_filter
                                              │
                                              ▼
                                       Container (Employee section) filters
                                       to show only that department
```

### Wireframe

```
+--+----------+------------------------------------------------------------------------+
|  |NAV       |                                                                        |
|  |          +------------------------------------------------------------------------+
|  |HR        |  +----------------------------------------------------------------+    |
|  |          |  |  CHART: Avg Tenure by Department                                |    |
|  |----------|  |  header: "Click a bar to filter by department"                  |    |
|  |FILTERS   |  |  [Horizontal Bar]                                               |    |
|  |          |  |  [click: cross-filter → dept_filter]                            |    |
|  |          |  +----------------------------------------------------------------+    |
|  |          |                                                                        |
|  |          |  CONTAINER: Employee Detail [filtered by dept_filter] (variant=filled) |
|  |          |  +----------------------------------+  +-----------------------------+  |
|  |          |  |  CHART: Compensation Distribution|  |  CHART: Performance Ratings  |  |
|  |          |  +----------------------------------+  +-----------------------------+  |
|  |          |  +----------------------------------------------------------------+    |
|  |          |  |  TABLE: Employees [sortable]                                    |    |
|  |          |  +----------------------------------------------------------------+    |
+--+----------+------------------------------------------------------------------------+
```

### Spec entry

```yaml
interactions:
  - type: cross-filter
    pattern: Single-Page Drill-Down
    trigger: click bar in "Avg Tenure by Department"
    source: Avg Tenure by Department (Graph)
    source_value: "y"
    control_id: dept_filter
    control_type: filter
    control_column: department
    targets: all components in "Employee Detail" container
    placement: container-level
    visible: true
```

### Code

```python
import vizro.actions as va
import vizro.models as vm
import vizro.plotly.express as px
from vizro.tables import dash_ag_grid

page = vm.Page(
    title="HR Overview",
    components=[
        vm.Graph(
            id="tenure_chart",
            header="Click a bar to filter by department",
            figure=px.bar("employees_agg", x="avg_tenure", y="department", orientation="h"),
            actions=va.set_control(control="dept_filter", value="y"),
        ),
        vm.Container(
            title="Employee Detail",
            variant="filled",
            components=[
                vm.Graph(id="comp_dist", figure=px.histogram("employees", x="compensation")),
                vm.Graph(id="perf", figure=px.box("employees", x="department", y="rating")),
                vm.AgGrid(id="emp_table", figure=dash_ag_grid("employees")),
            ],
            controls=[vm.Filter(id="dept_filter", column="department")],
        ),
    ],
)
```

### Key decisions

| Decision | Choice | Reasoning |
| --- | --- | --- |
| Filter scoped to container | Yes | Only the Employee Detail container is filtered; the bar chart at top stays unfiltered |
| Container `variant="filled"` | Recommended | Visually groups filtered components |
| Filter visible | Yes | User can change department from a dropdown without re-clicking |

---

## Pattern 3: Comparison Spotlight (cross-highlight)

**Domain example**: Country GDP rank — click a country bar to highlight its line in a bump chart.

### When to use

- Many entities shown at once; user wants to focus on one without losing the comparison context.
- "Which one stands out? Let me click to see it against the rest."
- The visual feedback IS the highlight — no filter, no navigation.

### When NOT to use

- User wants to filter data out (use Pattern 1, 2, or 4).
- Fewer than ~5 entities (highlighting adds little when everything is already legible).
- No clear "compare one vs all" mental model.

### Interaction flow

```
[Source chart with many entities] ──click entity──> sets highlight_param (visible=False)
                                                            │
                                                            ▼
                                              [Target chart] re-renders with that
                                              entity bolded, others faded
```

The intermediate control is a Parameter (not a Filter) because we are changing a chart **argument**, not the data.

### Wireframe

```
+--+----------+------------------------------------------------------------------------+
|  |NAV       |                                                                        |
|  |Countries |  +----------------------------------+  +-----------------------------+  |
|  |----------|  |  CHART: Life Exp by Country      |  |  CHART: GDP Rank Over Time   |  |
|  |FILTERS   |  |  header: "Click to highlight"    |  |  [Bump chart]                |  |
|  |Year      |  |  [Horizontal Bar]                |  |  (custom @capture("graph"))   |  |
|  |[v]       |  |  [click: highlight → hi_param]   |  |  [← highlight: hi_param]      |  |
|  |          |  +----------------------------------+  +-----------------------------+  |
+--+----------+------------------------------------------------------------------------+
```

### Spec entry

```yaml
interactions:
  - type: cross-highlight
    pattern: Comparison Spotlight
    trigger: click bar in "Life Exp by Country"
    source: Life Exp by Country (Graph)
    source_value: "y"              # country on y-axis (horizontal bar)
    control_id: highlight_country_param
    control_type: parameter
    targets: ["bump_chart.highlight_country"]
    placement: page-level
    visible: false                 # highlighting itself is the feedback
```

### Code

The target chart must be a custom chart with a `highlight_X` argument. See `dashboard-build/references/custom_charts_guide.md` ("Highlight-Aware Custom Charts") for the chart shape. The action wiring:

```python
import vizro.actions as va
import vizro.models as vm
import vizro.plotly.express as px

page = vm.Page(
    title="Country Comparison",
    components=[
        vm.Graph(
            id="life_exp_bar",
            header="Click a bar to highlight that country in the chart",
            figure=px.bar("gapminder_2007", x="lifeExp", y="country", orientation="h"),
            actions=va.set_control(control="highlight_country_param", value="y"),
        ),
        vm.Graph(
            id="bump_chart",
            figure=bump_chart_with_highlight(data_frame="gapminder"),  # custom @capture("graph")
        ),
    ],
    controls=[
        vm.Parameter(
            id="highlight_country_param",
            targets=["bump_chart.highlight_country"],
            selector=vm.RadioItems(options=["NONE", *all_country_names]),
            visible=False,
        ),
    ],
)
```

### Key decisions

| Decision | Choice | Reasoning |
| --- | --- | --- |
| Parameter (not Filter) | Required | We are changing a chart argument, not data. Data should NOT be filtered out — context matters |
| `visible=False` | Required | The highlight effect itself is the visual feedback |
| `"NONE"` in selector options | Required | Initial state — nothing highlighted. Also enables Vizro's "Reset controls" to clear highlight |
| Custom chart required | Yes | Built-in `px.bar`/`px.line` cannot express "highlight one trace" — needs `@capture("graph")` with `highlight_X` arg |

---

## Pattern 4: Multi-Dimensional Slice

**Domain example**: Scheduling (Day × Time heatmap → filtered appointments table).

### When to use

- 2+ categorical dimensions visualized together (heatmap, pivot).
- Users want to see the underlying records for a specific intersection.
- Clicking one cell should set ALL the dimensional filters at once.

### When NOT to use

- Only one dimension (use Pattern 2).
- Dimensions are continuous (this pattern is for discrete categories).

### Interaction flow

```
[Heatmap cell click] ──actions chain──> sets day_filter (dim 1)
                                  └──> sets time_filter (dim 2)
                                              │
                                              ▼
                                       [Table] filtered to that intersection
```

### Wireframe

```
+--+----------+------------------------------------------------------------------------+
|  |NAV       |                                                                        |
|  |          |  +----------------------------------------------------------------+    |
|  |Schedule  |  |  CHART: Appointment Density                                     |    |
|  |----------|  |  header: "Click a cell to filter appointments below"            |    |
|  |FILTERS   |  |  [Heatmap: day × time]                                          |    |
|  |          |  |  [click: cross-filter → day_filter + time_filter]               |    |
|  |          |  +----------------------------------------------------------------+    |
|  |          |  +----------------------------------------------------------------+    |
|  |          |  |  TABLE: Appointments [sortable]                                 |    |
|  |          |  |  [← filtered by: day_filter + time_filter]                      |    |
|  |          |  +----------------------------------------------------------------+    |
+--+----------+------------------------------------------------------------------------+
```

### Spec entry

```yaml
interactions:
  - type: cross-filter
    pattern: Multi-Dimensional Slice
    trigger: click cell in "Appointment Density" heatmap
    source: Appointment Density (Graph)
    source_value: ["x", "y"]           # actions chain — one per dimension
    control_id: [day_filter, time_filter]
    control_type: filter
    control_column: [day, time_slot]
    targets: [appointments_table]
    placement: page-level
    visible: true
```

### Code

```python
import vizro.actions as va
import vizro.models as vm
import vizro.plotly.express as px
from vizro.tables import dash_ag_grid

page = vm.Page(
    title="Appointments",
    components=[
        vm.Graph(
            id="heatmap",
            header="Click a cell to filter the appointments below",
            figure=px.density_heatmap("appointments", x="day", y="time_slot"),
            actions=[
                va.set_control(control="day_filter", value="x"),
                va.set_control(control="time_filter", value="y"),
            ],
        ),
        vm.AgGrid(id="appointments_table", figure=dash_ag_grid("appointments")),
    ],
    controls=[
        vm.Filter(id="day_filter", column="day", targets=["appointments_table"]),
        vm.Filter(id="time_filter", column="time_slot", targets=["appointments_table"]),
    ],
)
```

### Key decisions

| Decision | Choice | Reasoning |
| --- | --- | --- |
| Two separate Filters | Required | Each dimension needs its own control so it can be reset independently |
| Actions chain | Required | Both filters must be set on one click |
| Both filters visible | Recommended | Users can see the active slice |
| Target is the table only | Yes | Heatmap itself does not need to react to the click |

---

## Pattern 5: Select & Explore (self-highlight + cross-filter)

**Domain example**: Portfolio Analysis (click sector bar → bar highlights AND holdings table filters).

### When to use

- Source chart and target are on the same level (not overview → detail).
- Users benefit from seeing their selection visually confirmed in the source.
- Source needs immediate visual feedback (the highlight) AND must filter elsewhere.

### When NOT to use

- Source is purely an overview, target is detail → use Pattern 2.
- Source's visual feedback isn't needed (clicking a row and filtering a chart → use Pattern 2).

### Interaction flow

```
[Bar chart click] ──actions chain──> sets highlight_param (visible=False) ──> source chart self-highlights
                              └──> sets sector_filter ──> [target table] filters to that sector
```

### Wireframe

```
+--+----------+------------------------------------------------------------------------+
|  |NAV       |                                                                        |
|  |          |  +----------------------------------+  +-----------------------------+  |
|  |Portfolio |  |  CHART: Allocation by Sector     |  |  TABLE: Holdings             |  |
|  |----------|  |  header: "Click to select"       |  |  [← filtered by: sector]    |  |
|  |FILTERS   |  |  [Custom bar with highlight_X]   |  |                              |  |
|  |          |  |  [click: highlight + cross-filter]|  |                              |  |
|  |          |  +----------------------------------+  +-----------------------------+  |
+--+----------+------------------------------------------------------------------------+
```

### Spec entry

```yaml
interactions:
  - type: cross-highlight
    pattern: Select & Explore
    trigger: click bar in "Allocation by Sector"
    source: Allocation by Sector (Graph)
    source_value: "y"
    control_id: sector_highlight_param
    control_type: parameter
    targets: ["allocation_chart.highlight_sector"]
    placement: page-level
    visible: false
  - type: cross-filter
    pattern: Select & Explore
    trigger: click bar in "Allocation by Sector"
    source: Allocation by Sector (Graph)
    source_value: "y"
    control_id: sector_filter
    control_type: filter
    control_column: sector
    targets: [holdings_table]
    placement: page-level
    visible: true
```

### Code

```python
import vizro.actions as va
import vizro.models as vm
from vizro.tables import dash_ag_grid
# bar_with_highlight: custom @capture("graph") chart with a highlight_sector kwarg
# (see custom_charts_guide.md "Highlight-Aware Custom Charts" for the chart shape)

page = vm.Page(
    title="Portfolio",
    components=[
        vm.Graph(
            id="allocation_chart",
            header="Click a bar to select a sector and filter the table",
            figure=bar_with_highlight(data_frame="portfolio"),  # custom chart w/ highlight_sector
            actions=[
                va.set_control(control="sector_highlight_param", value="y"),
                va.set_control(control="sector_filter", value="y"),
            ],
        ),
        vm.AgGrid(id="holdings_table", figure=dash_ag_grid("holdings")),
    ],
    controls=[
        vm.Parameter(
            id="sector_highlight_param",
            targets=["allocation_chart.highlight_sector"],
            selector=vm.RadioItems(options=["NONE", *sectors]),
            visible=False,
        ),
        vm.Filter(id="sector_filter", column="sector", targets=["holdings_table"]),
    ],
)
```

### Key decisions

| Decision | Choice | Reasoning |
| --- | --- | --- |
| Custom chart required | Yes | The source self-highlights |
| Action order: highlight first, then filter | Recommended | Visual feedback should appear immediately on click |
| Parameter `visible=False`, Filter visible | Typical | The highlight is the parameter's feedback; the filter dropdown is useful for direct selection |

---

## Pattern 6: Data Export

**Domain example**: Any analyst-facing dashboard.

### When to use

- Users (typically analysts) need to download the filtered data for offline analysis.
- "I've drilled down to exactly what I need, now let me pull it into Excel."

### When NOT to use

- Executive dashboards where export is not expected.
- Dashboards with sensitive data that shouldn't leave the platform.

### Interaction flow

```
[Button click] ──> va.export_data() ──> downloads all on-page graphs/tables/figures as CSV
                                        (data reflects current filter/parameter state)
```

### Wireframe

```
+--+----------+------------------------------------------------------------------------+
|  |NAV       |                                                                        |
|  |          |  (existing page content above)                                         |
|  |----------|                                                                        |
|  |FILTERS   |  +----------------------------------------------------------------+    |
|  |          |  |  TABLE: Transactions (sortable, filtered by sidebar)            |    |
|  |          |  +----------------------------------------------------------------+    |
|  |          |  [BUTTON: Export data]                                                 |
+--+----------+------------------------------------------------------------------------+
```

### Spec entry

```yaml
interactions:
  - type: export_data
    pattern: Data Export
    trigger: click "Export data" button
    page: [Page Name]
```

### Code

```python
import vizro.actions as va
import vizro.models as vm

page = vm.Page(
    title="Transactions",
    components=[
        vm.Graph(figure=...),
        vm.AgGrid(figure=...),
        vm.Button(text="Export data", actions=va.export_data()),
    ],
)
```

### Key decisions

| Decision | Choice | Reasoning |
| --- | --- | --- |
| Button placement | Bottom of page or near the table | Logical reading order; users decide to export after reviewing |
| Button text | Clear and action-oriented (e.g. "Export data", "Download CSV") | Not "Submit" or "Button" |
| One button per page | Typical | Exports all data on the page |

---

## Action Mechanics Reference

Cross-cutting code patterns shared across the 6 named patterns.

### Export Data

```python
vm.Button(text="Export data", actions=va.export_data())
```

- Exports all graphs / tables / figures on the page as CSV (one file per component).
- Exported data reflects current Filter/Parameter state.
- Does NOT include client-side modifications (AG Grid filters, graph zoom).

### Cross-Filter from Table

```python
vm.AgGrid(
    header="Click a row to view details",
    figure=dash_ag_grid("reps_data"),
    actions=va.set_control(control="rep_filter", value="rep_name"),
)
vm.Filter(id="rep_filter", column="rep_name")
```

- **Trigger**: click or `Space` on a row.
- **`value`**: column name. Always taken from the clicked row's column, regardless of which cell was clicked.
- **`control`**: the `id` of the Filter.

### Cross-Filter from Graph

Two approaches depending on the column you want to filter on.

**Positional (simpler)** — use when the filter column is a positional axis (`x`, `y`, `z`, `lat`, `lon`):

```python
vm.Graph(
    figure=px.bar("pipeline", x="value", y="region", orientation="h"),
    actions=va.set_control(control="region_filter", value="y"),  # "y" = region
)
vm.Filter(id="region_filter", column="region")
```

**Via `custom_data`** — use when the filter column is encoded as something other than a positional axis (e.g. `color`):

```python
vm.Graph(
    figure=px.box("tips", x="tip", y="time", color="sex", custom_data="sex"),
    actions=va.set_control(control="sex_filter", value="sex"),
)
vm.Filter(id="sex_filter", column="sex")
```

For custom charts, the function signature must accept `custom_data`:

```python
@capture("graph")
def my_custom_chart(data_frame, custom_data, **kwargs):
    return px.scatter(data_frame, custom_data=custom_data, **kwargs)
```

### Cross-Highlight wiring

Cross-highlight is **cross-parameter** under the hood — the control is a Parameter, not a Filter.

```python
vm.Graph(
    id="source_chart",
    figure=px.bar("data", x="value", y="country", orientation="h"),
    actions=va.set_control(control="highlight_param", value="y"),
)
vm.Graph(
    id="target_chart",
    figure=my_chart_with_highlight(data_frame="data"),  # custom chart, highlight_country arg
)
vm.Parameter(
    id="highlight_param",
    targets=["target_chart.highlight_country"],
    selector=vm.RadioItems(options=["NONE", *country_names]),
    visible=False,
)
```

The custom chart shape (`highlight_X` argument, fade non-matching traces) belongs in [custom_charts_guide.md](../../dashboard-build/references/custom_charts_guide.md) under "Highlight-Aware Custom Charts". The action wiring is here.

### Cross-Filter Between Containers

Source in container A, Filter in container B → all components in container B are targets.

```python
vm.Container(
    components=[
        vm.AgGrid(figure=dash_ag_grid("tips"), actions=va.set_control(control="sex_filter", value="sex")),
    ],
)
vm.Container(
    components=[vm.Graph(figure=px.histogram("tips", x="tip"))],
    controls=[vm.Filter(id="sex_filter", column="sex")],  # scoped to this container
)
```

- When `targets` is omitted on a Filter inside a Container, it defaults to all components in that container.
- `variant="filled"` on the target container is recommended for visual clarity.

### Cross-Filter Between Pages

Source on Page 1, Filter on Page 2 with `show_in_url=True`.

```python
# Page 1
vm.AgGrid(
    actions=va.set_control(control="rep_filter", value="rep_name"),
)

# Page 2
vm.Page(
    title="Rep Detail",
    layout=vm.Flex(direction="column"),  # REQUIRED — back button needs natural height
    components=[
        vm.Button(text="← Back", href="/team-overview", variant="outlined"),
        vm.Container(layout=vm.Grid(...), components=[...]),
    ],
    controls=[vm.Filter(id="rep_filter", column="rep_name", show_in_url=True)],
)
```

- **`show_in_url=True`**: required. Without it, the cross-page drill-through silently fails.
- **Back button**: place as the first component on the target page. Use `href` (a navigation link), NOT an action.
- **`href` format**: page title slugified — lowercase, dashes for spaces, prefixed with `/`. Example: `"Team Overview"` → `"/team-overview"`.
- **Flex layout on target page**: required. In a Grid layout the back button occupies a full 140px+ row, wasting space. With Flex, the button takes natural height. Wrap the remaining content in a `vm.Container(layout=vm.Grid(...))` for precise positioning.

### Multi-Dimensional Cross-Filter

Actions chain on one source, one `set_control` per dimension, one Filter per dimension.

```python
vm.Graph(
    figure=px.density_heatmap("appointments", x="day", y="time_slot"),
    actions=[
        va.set_control(control="day_filter", value="x"),
        va.set_control(control="time_filter", value="y"),
    ],
)
vm.Filter(id="day_filter", column="day", targets=["appointments_table"])
vm.Filter(id="time_filter", column="time_slot", targets=["appointments_table"])
```

- Actions execute sequentially — the second `set_control` runs after the first completes.

### Actions Chains

Multiple actions on one trigger, sequential execution.

```python
vm.Graph(
    actions=[
        action_1,
        action_2,
        # ...
    ],
)
```

- Can mix built-in (`va.*`) and custom (`vm.Action`) actions in the same list.
- Action_2 runs only after action_1 completes — useful when one depends on the other's effect.
- Common combinations: self-highlight + cross-filter (Pattern 5), multi-dimensional (Pattern 4).

---

## Visual Affordances

Users need visible cues that a component is interactive.

### Source hints (`header`)

Add a short, action-oriented `header` on any Graph/AgGrid with `actions=`:

```python
# Good — short, action-oriented
vm.Graph(header="Click a bar to filter by region", ...)
vm.AgGrid(header="Click a row to view rep details", ...)

# Bad — verbose, vague
vm.Graph(header="This chart supports interactive cross-filtering capabilities", ...)
```

### Back button for cross-page drill-through

```python
vm.Button(text="← Back", href="/source-page-slug", variant="outlined")
```

- Place as the **first component** on the target page.
- Use `href` (navigation), NOT `actions=`.
- `variant="outlined"` keeps the back button visually secondary.
- The page MUST use `layout=vm.Flex(direction="column")` so the button takes natural height.

### Export button

```python
vm.Button(text="Export data", actions=va.export_data())
```

- Clear text. Avoid generic labels.

---

## Common Implementation Mistakes

| Mistake | Symptom | Fix |
| --- | --- | --- |
| Forgetting `custom_data` on graph cross-filter | Click does nothing when filter column is not a positional axis | Add `custom_data="column"` to the figure |
| Forgetting `id` on Filter / Parameter | `set_control` can't reference the control | Add explicit `id="my_filter"` |
| Forgetting `id` on target component | Filter / Parameter `targets` can't reach it | Add explicit `id="my_chart"` |
| Using deprecated `filter_interaction` | Deprecation warning or unexpected behavior | Use `va.set_control` instead |
| Forgetting `show_in_url=True` for cross-page | Drill-through silently fails | Add `show_in_url=True` on the target page's Filter |
| Forgetting `"NONE"` in highlight Parameter options | Chart starts in an unexpected highlighted state | Include `"NONE"` as the first option |
| Missing `header` hint on interactive source | User doesn't know the chart/table is clickable | Add `header="Click a bar to..."` |
| Missing back button on drill-through target | User feels trapped on the detail page | Add `vm.Button(text="← Back", href="/source-page", variant="outlined")` as the first component |
| Back button on a Grid-layout page | Button wastes a full 140px+ row | Use `layout=vm.Flex(direction="column")` on the page; wrap rest in a Container with Grid |
| Custom chart missing `custom_data` in signature | `custom_data` not passed to the plotly figure | Add `custom_data` to the function parameters |
| Wrapping built-in actions in `vm.Action` | Unexpected behavior or error | Pass built-in actions directly: `actions=va.export_data()` |
| Using a Filter when you wanted to highlight (Pattern 3) | Data is removed instead of styled | Use a Parameter targeting a custom chart's `highlight_X` arg, with `visible=False` |
