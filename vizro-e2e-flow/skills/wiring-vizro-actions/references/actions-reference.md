# Vizro Actions Reference

Full reference for the **wiring-vizro-actions** skill. Each named pattern below covers both design-phase decisions (when to use, wireframe, spec entry) and build-phase implementation (full code). Cross-cutting gotchas live in the **Common Implementation Mistakes** table at the bottom.

## Contents

- Core Concept (Source → Control → Target)
- Pattern 1: Hierarchical Drill-Down (cross-page)
- Pattern 2: Single-Page Drill-Down (container)
- Pattern 3: Comparison Spotlight (cross-highlight)
- Pattern 4: Multi-Dimensional Slice
- Pattern 5: Data Export
- Visual Affordances
- Common Implementation Mistakes

## Core Concept

All advanced interactions follow **Source → Control → Target**:

```
[Source]                [Control]                  [Target(s)]
 Graph     --click-->    Filter (id=...)            Graph
 AgGrid                  or Parameter      ---->    AgGrid
          va.set_control(control=..., value=...)    Figure
                          (visible=True/False)      Table
```

- **Sources** (for cross-filter / cross-highlight): `Graph` and `AgGrid` — both carry click-data (column values from the clicked point/cell). `Figure`, `Button`, and `Card` technically accept `actions=va.set_control(...)` but only with a hardcoded `value`, so they don't help with dynamic filtering.
- **Targets** (anything a Filter/Parameter can target): `Graph`, `AgGrid`, `Figure`, `Table` — the data-bearing components.
- The control is **always explicit** with an `id`. You never connect source to target directly.
- The source uses `va.set_control` (a built-in action). The control then drives the target.
- Targets are inferred from the control: a Filter's `targets` (or its container scope), a Parameter's `targets`.
- This shape composes: multiple sources can write to the same control; one source can chain multiple `set_control` calls.

## Pattern 1: Hierarchical Drill-Down (cross-page)

**Domain example**: Sales Pipeline (Region → Sales Rep → Deals).

### When to use

All two should be true — otherwise Pattern 2 or a sidebar `vm.Filter` is the right call.

- **Per-entity detail is rich enough to deserve its own page.** Multiple charts, a table, KPIs, possibly an export — too much to cram into a container on the overview.
- **Users complete a real workflow on the detail page.** They read multiple charts, examine a table, drill further — not just peek and bounce back.

### When NOT to use

- Detail fits in a container on the same page → use Pattern 2 (no nav, simpler).
- Few top-level groups (~5 or fewer) and a flat workflow → sidebar `vm.Filter` is simpler.
- Users only peek at the detail before returning → the page hop adds friction without payoff.

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

```markdown
<!-- spec/2_interaction_ux.md — Interactions section excerpt -->

## Interactions

### Region drill-down
- Type: cross-filter
- Pattern: Hierarchical Drill-Down
- Trigger: click bar in "Pipeline by Region"
- Source: Pipeline by Region (Graph)
- Source value: "y" (region on y-axis — horizontal bar)
- Control id: region_filter
- Control type: filter
- Control column: region
- Targets: all components in "Rep Breakdown" container
- Placement: container-level
- Visible: true

### Rep drill-through
- Type: cross-page-drill-through
- Pattern: Hierarchical Drill-Down
- Trigger: click row in "Sales Reps" table
- Source: Sales Reps (AgGrid)
- Source value: "rep_name"
- Control id: rep_filter
- Control type: filter
- Control column: rep_name
- Targets: all components on "Rep Detail" page
- Placement: page-level (Rep Detail)
- Visible: true
- Show in URL: true

### Export rep data
- Type: export_data
- Pattern: Hierarchical Drill-Down
- Trigger: click "Export data" button
- Page: Rep Detail
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
        # Pipeline Overview is the first page in Dashboard(pages=[...]), so its path is "/" — NOT "/pipeline-overview"
        vm.Button(text="← Back", href="/", variant="outlined"),
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
| `href` for the back button | Depends on which page in `Dashboard(pages=[...])` is the target | **The first page in the list has `path="/"` regardless of its title** — Vizro doesn't slugify the root. So if the source (Page 1) is the first entry, the back button is `href="/"`. For any later page, it's `/{title-lowercased-with-dashes}` (e.g. `"Team Overview"` → `/team-overview`). Use `href` (navigation), not `actions=`. |
| Horizontal bars | Always | Prevents crowded labels; `value="y"` for cross-filter |
| Page 2 Flex layout | Required | Back button needs natural height (Grid would waste a row) |
| Header hint on source | Required | User must know the component is clickable |
| Export on Page 2 only | Intentional | Detail page is where users export filtered data |

---

## Pattern 2: Single-Page Drill-Down (container)

**Domain example**: HR Dashboard (Department → Employee metrics).

### When to use

All three should be true — otherwise a sidebar `vm.Filter` is the right call.

- **Source chart earns its own screen space.** The chart is a primary viz users want regardless (not invented just to be a filter selector).
- **Users pick based on what they see, not from a known list.** Selection is driven by spotting something in the chart — an outlier, a peak, a spatial cluster, a ranking — rather than typing in a value the user already had in mind.
- **Detail fits in a container on the same page.** If it doesn't, use Pattern 1.

### When NOT to use

- The source chart exists only to be a control (no insight value of its own) → use a sidebar `vm.Filter`.
- Users already know which value they want → a sidebar dropdown is faster than reading the chart to find it.
- Few categories with no visual feature worth spotting → a sidebar dropdown is simpler.
- Detail content is too large for a container → use Pattern 1.

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
+----------+------------------------------------------------------------------------+
|NAV       |                                                                        |
|HR ●      |  HR (page header)                                                      |
|Other     |                                                                        |
|          |  +----------------------------------------------------------------+    |
|          |  |  CHART: Avg Tenure by Department                                |   |
|          |  |  header: "Click a bar to filter by department"                  |   |
|          |  |  [Horizontal Bar]                                               |   |
|          |  |  [click: cross-filter → dept_filter]                            |   |
|          |  +----------------------------------------------------------------+    |
|          |                                                                        |
|          |  CONTAINER: Employee Detail (variant=filled)                           |
|          |  [Dept Filter v]  ← scoped inside container, filters all 3 below       |
|          |  +----------------------------------+  +-----------------------------+ |
|          |  |  CHART: Compensation Distribution|  |  CHART: Performance Ratings | |
|          |  +----------------------------------+  +-----------------------------+ |
|          |  +----------------------------------------------------------------+    |
|          |  |  TABLE: Employees [sortable]                                    |   |
|          |  +----------------------------------------------------------------+    |
+----------+------------------------------------------------------------------------+
```

### Spec entry

```markdown
## Interactions

### Department drill-down
- Type: cross-filter
- Pattern: Single-Page Drill-Down
- Trigger: click bar in "Avg Tenure by Department"
- Source: Avg Tenure by Department (Graph)
- Source value: "y"
- Control id: dept_filter
- Control type: filter
- Control column: department
- Targets: all components in "Employee Detail" container
- Placement: container-level
- Visible: true
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
| `targets` omitted on container-scoped Filter | OK | A Filter declared inside `vm.Container(controls=[...])` defaults to all components in that container — no need to list each one |
| Container `variant="filled"` | Recommended | Visually groups filtered components |
| Filter visible | Yes by default; `visible=False` if the user explicitly asks for no dropdown | Visible gives an alternative reset path. |

---

## Pattern 3: Comparison Spotlight (cross-highlight)

**Domain example**: Country GDP rank — click a country bar to highlight its line in a bump chart.

### When to use

All three should be true — otherwise a Filter (sidebar or cross-filter) is the right call.

- **The user question is "this one vs the rest", not "just this one".** Removing the other entities would destroy the insight. The rest are comparison context, not noise.
- **Target chart is unreadable without spotlighting.** Many overlapping entities (a bump chart of 100 countries, a line chart of 50 sales reps) — no individual entity is legible without bringing it forward.
- **The user typically asks the question explicitly.** The chart already shows everything; the user opts in to "spotlight country X". Don't add Pattern 3 speculatively — wait for the user to ask for highlighting.

### When NOT to use

- User wants to see only the selected entity → use a Filter (sidebar `vm.Filter` or cross-filter, Pattern 1/2/4).
- Few entities (~5 or fewer) all already legible → no need to fade the rest.
- Each entity is independent (no "rest" to compare against) → highlighting adds nothing.
- The selected entity needs a different view (detail page, summary stats) → use Pattern 1 drill-through instead.

### Interaction flow

```
[Source chart with many entities] ──click entity──> sets highlight_param
                                                    (vm.Parameter, visible=False)
                                                            │
                                                            ▼
                                              [Target chart] re-renders with that
                                              entity bolded, others faded
```

The intermediate control is a **Parameter** (not a Filter) because we are changing a chart **argument**, not the data.

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

```markdown
## Interactions

### Country highlight
- Type: cross-highlight
- Pattern: Comparison Spotlight
- Trigger: click bar in "Life Exp by Country"
- Source: Life Exp by Country (Graph)
- Source value: "y" (country on y-axis — horizontal bar)
- Control id: highlight_country_param
- Control type: parameter
- Targets: `bump_chart.highlight_country`
- Placement: page-level
- Visible: false (highlighting itself is the feedback)
```

### Code

The target chart must be a custom `@capture("graph")` function with a `highlight_X` kwarg defaulting to `None` (Vizro maps the selector's `"NONE"` option to Python `None`). When `highlight_X is None`, nothing is emphasized. When it is set, the matching entity is bolded; the rest stay faded.

**Target chart shape — pick the variant that matches the data:**

```python
# Variant A — boolean color (bar / scatter): one row per data point, one entity to bring forward
from vizro.models.types import capture
import vizro.plotly.express as px

@capture("graph")
def scatter_with_highlight(data_frame, highlight_country=None):
    is_highlighted = data_frame["country"] == highlight_country
    fig = px.scatter(
        data_frame, x="gdpPercap", y="lifeExp", size="pop", size_max=60,
        opacity=0.3,
        color=is_highlighted,
        category_orders={"color": [False, True]},  # locks highlighted trace at index 1
    )
    if highlight_country is not None:
        fig.update_traces(selector=1, marker={"line_width": 2, "opacity": 1})
    fig.update_layout(showlegend=False)
    return fig

# Variant B — name selector (line / bump): each entity is its own trace
@capture("graph")
def bump_chart_with_highlight(data_frame, highlight_country=None):
    rank = data_frame.groupby("year")["lifeExp"].rank(method="dense", ascending=False)
    fig = px.line(data_frame, x="year", y=rank, color="country", markers=True)
    fig.update_traces(opacity=0.3, line_width=2)  # fade all
    if highlight_country is not None:
        fig.update_traces(selector={"name": highlight_country}, opacity=1, line_width=3)
    return fig
```

**Page wiring** — source bar fires `set_control` on a hidden Parameter that targets the bump chart's `highlight_country`:

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
            figure=bump_chart_with_highlight(data_frame="gapminder"),
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
| `"NONE"` in selector options | Required | First option becomes the "no highlight" target. Vizro restores it on any clear path: clicking the same bar a second time (Plotly's default `clickmode="event+select"` deselects → `set_control` sees `None` → resets to first option) or the "Reset controls" button. Without it, both paths would restore to whichever option is first alphabetically. |
| Custom chart required | Yes | Built-in `px.bar`/`px.line` cannot express "highlight one trace" — needs `@capture("graph")` with `highlight_X` arg |

---

## Pattern 4: Multi-Dimensional Slice

**Domain example**: Scheduling (Day × Time heatmap → filtered appointments table).

### When to use

All three should be true — otherwise two independent sidebar `vm.Filter`s do the job.

- **The chart visualizes the intersection of 2+ discrete dimensions.** Heatmap, density grid, pivot — the value at row × column is the insight, not the marginals alone.
- **Users pick the cell based on what they see at the intersection.** They notice "Monday at 10am is the hottest cell" and click it. Without the viz, they'd guess-and-check across two dropdowns.
- **One click should commit both dimensions atomically.** Picking row then column via separate sidebar filters is two interactions and loses the spatial context between them.

### When NOT to use

- Only one dimension that matters → Pattern 2 or sidebar `vm.Filter`.
- Dimensions are independent (no insight from the intersection) → two separate sidebar `vm.Filter`s.
- Users already know the cell coordinates ahead of time → sidebar dropdowns are faster.
- Dimensions are continuous (this pattern is for discrete cells).

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

```markdown
## Interactions

### Day + time slice
- Type: cross-filter
- Pattern: Multi-Dimensional Slice
- Trigger: click cell in "Appointment Density" heatmap
- Source: Appointment Density (Graph)
- Source value: `["x", "y"]` (actions chain — one per dimension)
- Control id: `[day_filter, time_filter]`
- Control type: filter
- Control column: `[day, time_slot]`
- Targets: `[appointments_table]`
- Placement: page-level
- Visible: true
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

## Pattern 5: Data Export

**Domain example**: Any analyst-facing dashboard.

### When to use

All three should be true — otherwise skip the export button.

- **Users have a downstream workflow outside the dashboard.** Excel modeling, sharing a slice with someone offline, feeding another tool — the dashboard isn't the final destination for the analysis.
- **The exact filtered slice they're viewing is what they want to export.** Not "all data ever" (in which case they should hit the source system directly).
- **The analyst persona is explicit in the requirements.** Don't add export speculatively — wait for the user to call out the offline workflow.

### When NOT to use

- Executive / view-only dashboards — no offline workflow expected.

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

```markdown
## Interactions

### Page data export
- Type: export_data
- Pattern: Data Export
- Trigger: click "Export data" button
- Page: [Page Name]
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
# If the source page is the FIRST page in Dashboard(pages=[...]):
vm.Button(text="← Back", href="/", variant="outlined")

# If the source page is a LATER page (title "Team Overview" -> slug "team-overview"):
vm.Button(text="← Back", href="/team-overview", variant="outlined")
```

- **`href` depends on page order, not title.** Vizro assigns `path="/"` to the first page in `Dashboard(pages=[...])` regardless of its title; subsequent pages get `/{title-lowercased-with-dashes}`. So if the source page is `pages[0]` the back button is `href="/"`, otherwise it's `/{title-slug}`. Hardcoding `/{title-slug}` for a first page produces a broken link.
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
| Forgetting `custom_data` on graph cross-filter | Click does nothing when filter column is not on a positional axis (`x`/`y`/`z`/`lat`/`lon`) | Add `custom_data="column"` to the figure and use `value="column"` in `set_control`. For a custom `@capture("graph")` function the signature must also accept `custom_data` (`def my_chart(data_frame, custom_data, **kwargs)`) — otherwise the callback fires a 500 |
| Forgetting `id` on Filter / Parameter | `set_control` can't reference the control | Add explicit `id="my_filter"` |
| Forgetting `id` on target component | Filter / Parameter `targets` can't reach it | Add explicit `id="my_chart"` |
| Using deprecated `filter_interaction` | Deprecation warning or unexpected behavior | Use `va.set_control` instead |
| Forgetting `show_in_url=True` for cross-page | `ValueError` at build time (app won't start) | Add `show_in_url=True` on the target page's Filter |
| Forgetting `"NONE"` in highlight Parameter options | Chart starts in an unexpected highlighted state | Include `"NONE"` as the first option |
| Missing `header` hint on interactive source | User doesn't know the chart/table is clickable | Add `header="Click a bar to..."` |
| Missing back button on drill-through target | User feels trapped on the detail page | Add `vm.Button(text="← Back", href=..., variant="outlined")` as the first component. **`href="/"` if the source is the first page in `Dashboard(pages=[...])`; `href="/<title-slug>"` otherwise.** |
| Back button on a Grid-layout page | Button wastes a full 140px+ row | Use `layout=vm.Flex(direction="column")` on the page; wrap rest in a Container with Grid |
| Custom chart missing `custom_data` in signature | `custom_data` not passed to the plotly figure | Add `custom_data` to the function parameters |
| Wrapping built-in actions in `vm.Action` | Unexpected behavior or error | Pass built-in actions directly: `actions=va.export_data()` |
| Using a Filter when you wanted to highlight (Pattern 3) | Data is removed instead of styled | Use a Parameter targeting a custom chart's `highlight_X` arg, with `visible=False` |
