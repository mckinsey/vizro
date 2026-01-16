# Layout Patterns Guide

Deep guidance for Step 2: Designing Layout & Interactions.

## Contents

- Layout System Overview
- Component Sizing Guidelines
- Wireframe Templates
- Container Patterns
- Filter and Parameter Placement
- Visual Hierarchy Principles
- Common Layout Mistakes
- Vizro-Specific Constraints

## Layout System Overview

Vizro provides two layout options:

- **Grid**: Precise control over component placement and sizing (recommended)
- **Flex**: Automatic vertical stacking with spacing (simple pages only)

**Recommendation**: Use Grid for most dashboards. Use Flex only for very simple single-column pages.

### Grid Concept

The grid divides page width into columns. Components are placed by specifying which columns they occupy. Height is controlled by how many **rows** a component spans.

**Key principles**:

- **12 columns recommended** (not enforced) - provides flexibility with many divisors (1, 2, 3, 4, 6, 12)
- Any column count works if there's good reason (e.g., 8 columns for simpler layouts)
- Control height by giving components more rows
- Each row is 140px tall (use `row_min_height="140px"`)
- Component height = rows × 140px

**Note**: All examples in this guide use 12 columns as a comprehensive default, but adapt as needed.

## Component Sizing Guidelines

Based on 12-column grid:

| Component   | Columns   | Rows | Min Height |
| ----------- | --------- | ---- | ---------- |
| KPI Card    | 3         | 1    | 140px      |
| Small Chart | 4         | 3    | 420px      |
| Large Chart | 6         | 4-5  | 560-700px  |
| Table       | 12 (full) | 4-6  | 560-840px  |

**Exceptions** - size based on content to render:

- Text-heavy Card → treat like a chart (3+ rows)
- Small Table (less than 5 columns) → doesn't need full width
- Button → 1 row is enough

**Flexible Width Distributions** (12-column advantage):

12 columns allows uneven widths since 12 has many divisors (1, 2, 3, 4, 6, 12):

| Layout                 | Column Distribution |
| ---------------------- | ------------------- |
| 3 equal charts         | 4 + 4 + 4           |
| Primary + 2 secondary  | 6 + 3 + 3           |
| Two-thirds + one-third | 8 + 4               |
| Two equal charts       | 6 + 6               |
| 4 KPI cards            | 3 + 3 + 3 + 3       |

## Wireframe Templates

### Component Labels for Wireframes

| Label         | Description                                                            |
| ------------- | ---------------------------------------------------------------------- |
| **KPI**       | Metric cards                                                           |
| **CHART**     | Visualizations with type: `[Line chart]`, `[Bar chart]`, `[Histogram]` |
| **TABLE**     | Data tables with features: `[sortable]`, `[pagination]`                |
| **CONTAINER** | Groups components, can have own filters/parameters                     |
| **TABS**      | Multiple views with tab labels                                         |
| **FILTER**    | In left panel (global) or above container (scoped)                     |
| **PARAMETER** | In left panel (global) or above container (scoped)                     |
| **ACTIONS**   | Buttons for export, drill-down, etc.                                   |

### Interaction Annotations

- `[↗ click: drill-down]` - Clicking navigates to detail
- `[hover: tooltip]` - Hovering shows information
- `[↗ click: toggle series]` - Clicking toggles chart elements
- `[sortable columns]` - Interactive table sorting

### Wireframing Guidelines

1. Use three-column layout: icon nav | left panel | main content
1. Label sections: KPI, CHART, TABLE, FILTER, PARAMETER, CONTAINER, TABS
1. Indicate chart types: `[Line chart]`, `[Bar chart]`, `[Histogram]`
1. Show hierarchy through box sizes (larger = more important)
1. Global filters/parameters in left panel, container-specific above containers
1. **Full-width charts**: Use ONLY for timeseries line charts
1. Most charts should be side-by-side (2-3 per row)

### Template 1: KPIs + Charts + Table

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

### Template 2: Full-Width Timeseries + Container

```
+--+----------+------------------------------------------------------------------------+
|  |NAV       |                                                                        |
|  |          +------------------------------------------------------------------------+
|  |Overview  |  +---------------------------------------------------------------------+|
|  |Details   |  |                                                                     ||
|  |          |  |  CHART: Revenue Trend [Timeseries Line - Full Width]                ||
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

### Template 3: Tabs for Multiple Views

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

## Container Patterns

### When to Use Containers

| Scenario                  | Use Container? |
| ------------------------- | -------------- |
| Group related charts      | Yes            |
| Section needs own filters | Yes            |
| Visual separation needed  | Yes            |
| Simple sequential layout  | No             |

### Container Styling Options

| Style    | Use Case                        |
| -------- | ------------------------------- |
| Plain    | No visual styling (default)     |
| Filled   | Background fill for emphasis    |
| Outlined | Border outline (major sections) |

## Filter and Parameter Placement

### Decision Tree

```
Is this filter needed across multiple visualizations?
├─ YES → Page-level filter (left sidebar)
└─ NO → Container-level filter (above container in main area)
```

**Page-level filters**: Always in left collapsible sidebar **Container filters**: Above the container they control

### Filter Selector Selection

**IMPORTANT**: Choose the appropriate selector type based on the data - don't default to Dropdown for everything.

| Data Type      | Selector        | When to Use                              |
| -------------- | --------------- | ---------------------------------------- |
| 2-3 options    | **RadioItems**  | Few mutually exclusive choices           |
| 4-7 options    | Dropdown        | Moderate number of options               |
| 8+ options     | Dropdown        | Many options (with search)               |
| Yes/No, On/Off | **Checklist**   | Boolean or toggle selections             |
| Numeric range  | **RangeSlider** | Price, quantity, score ranges            |
| Single number  | **Slider**      | Threshold, limit, single value selection |
| Date           | **DatePicker**  | Single date or date range selection      |

**Examples**:

- Region filter (North, South, East, West) → **RadioItems** (4 options, mutually exclusive)
- Category filter (10+ categories) → Dropdown
- Price range ($0-$1000) → **RangeSlider**
- Year filter (2020-2025) → **Slider** or **DatePicker**
- Active/Inactive status → **RadioItems** or **Checklist**

## Visual Hierarchy Principles

### F-Pattern Priority

Users scan in an F-shape: left to right, then down the left side.

```
+------------------+------------------+
| MOST IMPORTANT   | SECOND           |
| (top-left)       | (top-right)      |
+------------------+------------------+
| THIRD            | FOURTH           |
| (middle-left)    | (middle-right)   |
+------------------+------------------+
| SUPPORTING       | LEAST IMPORTANT  |
| (bottom-left)    | (bottom-right)   |
+------------------+------------------+
```

### Z-Pattern for Scanning

For sparse layouts with few elements, users scan in a Z-shape:

- Place critical KPIs top-left (natural eye starting point)
- Secondary metrics top-right
- Supporting details below
- Least important information bottom-right

### Size Indicates Importance

- **Primary metrics**: Larger cells (6 columns, half width)
- **Secondary metrics**: Medium cells (4 columns, one-third)
- **Supporting details**: Smaller cells (3 columns, quarter width)

## Common Layout Mistakes

### 1. Charts Too Small

**Problem**: Charts crammed into small spaces **Solution**: Minimum 4 columns × 3 rows for any chart

### 2. Everything Full-Width

**Problem**: Every chart spans all columns **Solution**: Only timeseries line charts should be full-width

### 3. No Visual Grouping

**Problem**: 10 charts with no clear sections **Solution**: Use containers to group related content

### 4. Filters in Main Area

**Problem**: Filters placed among charts **Solution**: Page filters in left sidebar; container filters above container

## Vizro-Specific Constraints

1. **Page Navigation**: Automatic sidebar (built-in, not customizable)
1. **Page Filters/Parameters**: MUST be in collapsible left sidebar
1. **Layouts**: Use Grid or Flex only (no absolute positioning)
1. **Components**: Limited to `Graph`, `AgGrid`, `Card`, `Figure`
1. **Containers**: Can use `Tabs` for organizing content
1. **Actions**: Export, filter, and parameter actions only

**Important**: Do not use emojis in dashboard implementations.

## Reference

- **Layouts**: https://vizro.readthedocs.io/en/latest/pages/user-guides/layouts/
- **Containers**: https://vizro.readthedocs.io/en/stable/pages/user-guides/container/
