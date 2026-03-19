# Wireframe Templates & Interaction Annotations

Design-phase reference for creating dashboard wireframes. For grid system, component sizing, and filter placement rules, load the **designing-vizro-layouts** skill.

**When to read:** Step 2 — when creating ASCII wireframes for user approval.

## Wireframe labels

| Label        | Description                                     |
| ------------ | ----------------------------------------------- |
| KPI          | Metric cards                                    |
| CHART        | Visualizations (type: [Line], [Bar], etc.)      |
| TABLE        | Data tables (sortable, pagination)              |
| CONTAINER    | Groups; can have own filters                    |
| TABS         | Multiple views with tab labels                  |
| FILTER/PARAM | Left panel (global) or above container (scoped) |

## Wireframing Guidelines

1. Use three-column layout: icon nav | left panel | main content
1. Use the labels above to annotate each section
1. Indicate chart types: `[Line chart]`, `[Bar chart]`, `[Histogram]`
1. Show hierarchy through box sizes (larger = more important)
1. Global filters/parameters in left panel, container-specific above containers
1. **Full-width charts**: Use ONLY for time-series line charts
1. Most charts should be side-by-side (2-3 per row)

## Interaction Annotations

- `[click: drill-down]` - Clicking navigates to detail
- `[hover: tooltip]` - Hovering shows information
- `[click: toggle series]` - Clicking toggles chart elements
- `[sortable columns]` - Interactive table sorting

## Template 1: KPIs + Charts + Table

```
+--+----------+------------------------------------------------------------------------+
|  |NAV       |                                                                        |
|  |          +------------------------------------------------------------------------+
|  |Page 1    |  +-------------+  +-------------+  +-------------+  +-------------+    |
|  |Page 2    |  | KPI 1       |  | KPI 2       |  | KPI 3       |  | KPI 4       |    |
|  |Page 3    |  | (3 cols)    |  | (3 cols)    |  | (3 cols)    |  | (3 cols)    |    |
|  |          |  +-------------+  +-------------+  +-------------+  +-------------+    |
|  |----------|                                                                        |
|  |FILTERS   |  +----------------------------------+  +-----------------------------+  |
|  |          |  |                                  |  |                             |  |
|  |Date      |  |  CHART: Primary Visualization    |  |  CHART: Secondary           |  |
|  |[v]       |  |  [Bar chart]                     |  |  [Line chart]               |  |
|  |          |  |  (6 cols, 3 rows)                |  |  (6 cols, 3 rows)           |  |
|  |Region    |  +----------------------------------+  +-----------------------------+  |
|  |[v]       |                                                                        |
|  |          |  +---------------------------------------------------------------------+|
|  |Category  |  |                                                                     ||
|  |[v]       |  |  TABLE: Detail Data (12 cols, 2 rows)                               ||
|  |          |  |  [sortable, filterable]                                             ||
|  |          |  +---------------------------------------------------------------------+|
+--+----------+------------------------------------------------------------------------+
```

## Template 2: Full-Width Time-series + Container

```
+--+----------+------------------------------------------------------------------------+
|  |NAV       |                                                                        |
|  |          +------------------------------------------------------------------------+
|  |Overview  |  +---------------------------------------------------------------------+|
|  |Details   |  |                                                                     ||
|  |          |  |  CHART: Revenue Trend [Time-series Line - Full Width]                ||
|  |----------|  |  (12 cols, 3 rows)                                                  ||
|  |FILTERS   |  |  [hover: tooltip | click: drill to detail]                          ||
|  |          |  +---------------------------------------------------------------------+|
|  |Year      |                                                                        |
|  |[v]       |  CONTAINER: Regional Breakdown (12 cols, 3 rows)                       |
|  |          |  [Container Filter: Region v]                                          |
|  |Quarter   |  +------------------+  +------------------+  +------------------------+|
|  |[v]       |  |                  |  |                  |  |                        ||
|  |          |  |  CHART: By Region|  |  CHART: By Product| |  TABLE: Top Items      ||
|  |          |  |  [Bar chart]     |  |  [Pie chart]     |  |  [sortable]            ||
|  |          |  |  (4 cols)        |  |  (4 cols)        |  |  (4 cols)              ||
|  |          |  +------------------+  +------------------+  +------------------------+|
+--+----------+------------------------------------------------------------------------+
```

## Template 3: Tabs for Multiple Views

```
+--+----------+------------------------------------------------------------------------+
|  |NAV       |                                                                        |
|  |          +------------------------------------------------------------------------+
|  |Dashboard |  TABS: [Overview] [By Region] [By Product] [Export]                    |
|  |          |  +---------------------------------------------------------------------+|
|  |----------|  | TAB CONTENT: Overview                                               ||
|  |FILTERS   |  |                                                                     ||
|  |          |  |  +-------------+  +-------------+  +-------------+                  ||
|  |Date      |  |  | KPI 1       |  | KPI 2       |  | KPI 3       |                  ||
|  |[v]       |  |  +-------------+  +-------------+  +-------------+                  ||
|  |          |  |                                                                     ||
|  |          |  |  +----------------------------------+  +---------------------------+||
|  |          |  |  |  CHART: Main Metric              |  |  CHART: Trend             |||
|  |          |  |  +----------------------------------+  +---------------------------+||
|  |          |  +---------------------------------------------------------------------+|
+--+----------+------------------------------------------------------------------------+
```
