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
|  |[v]       |  |  CHART: Revenue Trend [Line chart]                                  ||
|  |          |  |  [hover: tooltip | ↗ click: drill to detail]                       ||
|  |Region    |  +---------------------------------------------------------------------+|
|  |[v]       |                                                                        |
|  |          |  CONTAINER: Sales Analysis                                            |
|  |Category  |  [Container Filters: Region ▼  Product ▼]                             |
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
|  |----------|  |  PARAMETER: Metric Type [dropdown: Revenue | Profit | Volume]       ||
|  |FILTERS:  |  |                                                                     ||
|  |          |  |  +-------------------------------+  +---------------------------+  ||
|  |Date      |  |  |                               |  |                           |  ||
|  |[v]       |  |  |  CHART: Main Metric           |  |  CHART: Comparison        |  ||
|  |          |  |  |  [Area chart]                 |  |  [Bar chart]              |  ||
|  |Status    |  |  |  [↗ click: toggle series]     |  |  [hover: show values]     |  ||
|  |[v]       |  |  +-------------------------------+  +---------------------------+  ||
|  |          |  |                                                                     ||
|  |          |  |  CONTAINER: Detailed Breakdown                                      ||
|  |          |  |  [Container Filters: Category ▼]                                    ||
|  |          |  |  +----------------------------------------------------------------+  ||
|  |          |  |  |  CHART: Distribution [Histogram]                               |  ||
|  |          |  |  +----------------------------------------------------------------+  ||
|  |          |  +---------------------------------------------------------------------+|
+--+----------+------------------------------------------------------------------------+
```

## Structure Components

**Three-column layout**:
- **Leftmost (icon nav)**: Navigation icons vertically stacked
- **Middle (left panel)**: Dropdown navigation + global filters below separator
- **Right (main content)**: Dashboard components in grid layout

**Component types**:
- **KPI**: Metric cards
- **CHART**: Visualizations with type in brackets `[Line chart]`, `[Bar chart]`, `[Donut chart]`, etc.
- **TABLE**: Data tables with features in brackets `[sortable columns]`, `[pagination]`
- **CONTAINER**: Groups components, can have own filters above
- **TABS**: Multiple views with tab labels at top
- **ACTIONS**: Buttons for export, drill-down, etc.
- **FILTER**: In left panel (global) or above container (container-specific)
- **PARAMETER**: Changes chart arguments (e.g., metric type, aggregation level)

**Interactions** (show with annotations):
- `[↗ click: drill-down]` - Clicking navigates to detail
- `[hover: tooltip]` - Hovering shows information
- `[↗ click: toggle series]` - Clicking toggles chart elements
- `[sortable columns]` - Interactive table sorting

## Guidelines

1. Three-column layout: icon nav | left panel (dropdown + filters) | main content
2. Label sections: KPI, CHART, TABLE, FILTER, PARAMETER, ACTIONS, CONTAINER, TABS
3. Indicate chart types in brackets: `[Line chart]`, `[Bar chart]`, `[Histogram]`
4. Show hierarchy through box sizes (larger = more important)
5. Global filters in left panel, container filters above containers
6. Annotate interactions: `[↗ click: action]`, `[hover: behavior]`

## Optional: HTML Wireframe

After ASCII approval, create HTML wireframe for stakeholder browser preview:
- Three-column flexbox layout (60px icon nav + 220px left panel + flex:1 main)
- 12-column grid in main content area
- Grayscale only, placeholder boxes for charts

## Implementation Mapping

- **Icon nav** → Top-level page navigation
- **Left panel dropdown** → Sub-navigation within section
- **Global filters** (left panel) → Page-level data filtering
- **Container filters** (above containers) → Section-specific data filtering
- **Grid layout** → 12-column system (span-12 = full, span-6 = half, span-4 = third, etc.)
- **Interactions** → Click handlers, hover states, navigation actions

For implementation guidance, see Step 9 (Build Dashboard) in dashboard-design skill.
