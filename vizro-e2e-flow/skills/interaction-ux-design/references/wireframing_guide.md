# Dashboard Wireframing Guide

## Purpose

Create low-fidelity dashboard wireframes using ASCII diagrams for rapid iteration and stakeholder feedback.

**Note**: This guide focuses on a three-column dashboard structure optimized for Vizro implementation (see dashboard-implementation skill for details). If you have strong design reasons to use a different layout structure, diverge as needed to meet user requirements.

## Three-Column Dashboard Structure

**Example 1: Basic Structure with Containers**

```
+--+----------+------------------------------------------------------------------------+
|🏠|Analytics |                                                                        |
|📊| v        +------------------------------------------------------------------------+
|📈|Overview  |  +-------------------------+  +-----------------+  +-----------------+  |
|📋|Reports   |  |                         |  |                 |  |                 |  |
|  |Customers |  |  KPI 1                  |  |  KPI 2          |  |  KPI 3          |  |
|  |          |  |  [↗ click: drill-down]  |  |                 |  |                 |  |
|  |----------|  +-------------------------+  +-----------------+  +-----------------+  |
|  |FILTERS:  |                                                                        |
|  |          |  +---------------------------------------------------------------------+|
|  |Year      |  |                                                                     ||
|  |[v]       |  |  CHART: Revenue Trend [Timeseries Line - Full Width]                ||
|  |          |  |  [hover: tooltip | ↗ click: drill to detail]                       ||
|  |Region    |  +---------------------------------------------------------------------+|
|  |          |  NOTE: Full-width ONLY for timeseries line charts                     |
|  |[v]       |                                                                        |
|  |          |  CONTAINER: Sales Analysis                                            |
|  |Category  |  [Container Parameters: Metric ▼] [Container Filters: Region ▼]       |
|  |[v]       |  +---------------------------------+  +-------------------------------+|
|  |          |  |                                 |  |                               ||
|  |          |  |  CHART: By Region               |  |  TABLE: Top Products          ||
|  |          |  |  [Horizontal bar chart]         |  |  [sortable columns]           ||
|  |          |  +---------------------------------+  +-------------------------------+|
|  |          |                                                                        |
|  |          |  CONTAINER: Customer Insights                                          |
|  |          |  [Container Filters: Segment ▼]                                        |
|  |          |  +------------------+  +------------------+  +-----------------------+  |
|  |          |  |  KPI Card        |  |  KPI Card        |  |  [ACTIONS]            |  |
|  |          |  |                  |  |                  |  |  Export Data          |  |
|  |          |  +------------------+  +------------------+  +-----------------------+  |
+--+----------+------------------------------------------------------------------------+
```

**Example 2: Tabs, Parameters, and Advanced Interactions**

```
+--+----------+------------------------------------------------------------------------+
|🏠|Dashboard |                                                                        |
|📊| v        +------------------------------------------------------------------------+
|📈|Home      |  TABS: [Overview] [Details] [Export]                                   |
|📋|Analysis  |  +---------------------------------------------------------------------+|
|⚙️|Settings  |  | TAB CONTENT: Overview                                              ||
|  |          |  |                                                                     ||
|  |----------|  |  +-------------------------------+  +---------------------------+  ||
|  |PARAMS:   |  |  |                               |  |                           |  ||
|  |          |  |  |  CHART: Main Metric           |  |  CHART: Comparison        |  ||
|  |Metric    |  |  |  [Area chart]                 |  |  [Bar chart]              |  ||
|  |[v]       |  |  |  [↗ click: toggle series]     |  |  [hover: show values]     |  ||
|  |          |  |  +-------------------------------+  +---------------------------+  ||
|  |----------|  |                                                                     ||
|  |FILTERS:  |  |  CONTAINER: Detailed Breakdown                                      ||
|  |          |  |  [Container Parameters: Bin Size ▼] [Container Filters: Category ▼] ||
|  |Date      |  |  +----------------------------------------------------------------+  ||
|  |[v]       |  |  |  CHART: Distribution [Histogram]                               |  ||
|  |          |  |  +----------------------------------------------------------------+  ||
|  |Status    |  +---------------------------------------------------------------------+|
|  |[v]       |                                                                        |
+--+----------+------------------------------------------------------------------------+
```

## Structure Components

**Three-column layout**:

- **Leftmost (icon nav)**: Navigation icons vertically stacked
- **Middle (left panel)**: Dropdown navigation + global parameters + global filters below separator
- **Right (main content)**: Dashboard components in grid layout

**Component types**:

- **KPI**: Metric cards
- **CHART**: Visualizations with type in brackets `[Line chart]`, `[Bar chart]`, `[Donut chart]`, etc.
- **TABLE**: Data tables with features in brackets `[sortable columns]`, `[pagination]`
- **CONTAINER**: Groups components, can have own parameters and filters above
- **TABS**: Multiple views with tab labels at top
- **ACTIONS**: Buttons for export, drill-down, etc.
- **FILTER**: In left panel (global page filters) or above container (container-specific filters)
- **PARAMETER**: In left panel (global page parameters) or above container (container-specific parameters). Changes chart arguments (e.g., metric type, aggregation level, bin size)

**Interactions** (show with annotations):

- `[↗ click: drill-down]` - Clicking navigates to detail
- `[hover: tooltip]` - Hovering shows information
- `[↗ click: toggle series]` - Clicking toggles chart elements
- `[sortable columns]` - Interactive table sorting
- etc.

## Guidelines

1. Three-column layout: icon nav | left panel (dropdown + parameters + filters) | main content
1. Label sections: KPI, CHART, TABLE, FILTER, PARAMETER, ACTIONS, CONTAINER, TABS
1. Indicate chart types in brackets: `[Line chart]`, `[Bar chart]`, `[Histogram]`
1. Show hierarchy through box sizes (larger = more important)
1. Global page parameters and filters in left panel, container-specific filters/parameters above containers
1. Annotate interactions: `[↗ click: action]`, `[hover: behavior]`
1. **Full-width charts**: Use ONLY for timeseries line charts (e.g., `[Timeseries Line - Full Width]`). Most charts should be side-by-side (2-3 per row)

## Optional: HTML Wireframe

After ASCII approval, create HTML wireframe for stakeholder browser preview:

- Three-column flexbox layout (60px icon nav + 220px left panel + flex:1 main)
- 12-column grid in main content area
- Grayscale only, placeholder boxes for charts

For implementation guidance after wireframing is complete, see Step 9 (Build Dashboard) in dashboard-design skill.
