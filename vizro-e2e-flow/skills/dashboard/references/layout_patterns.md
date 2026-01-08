# Layout Patterns Guide

Deep guidance for Phase 2: Designing Layout & Interactions.

## Contents

- Vizro Layout System (Grid vs Flex)
- Grid Layout Fundamentals (configuration, sizing, row height)
- Wireframe Templates (component labels, interaction annotations, guidelines)
- Container Patterns (when to use, scoped filters, styling)
- Filter and Parameter Placement
- Visual Hierarchy Principles (F-pattern, Z-pattern)
- Common Layout Mistakes
- Vizro-Specific Constraints
- Reference Links

## Vizro Layout System

Vizro provides two layout options:

- **Grid**: Precise control over component placement and sizing
- **Flex**: Automatic vertical stacking with spacing

**Recommendation**: Use Grid for most dashboards. Use Flex only for very simple pages.

## Grid Layout Fundamentals

### Configuration Structure

```python
vm.Page(
    title="Dashboard",
    layout=vm.Grid(
        grid=[
            [0, 0, 1, 1],  # Row 1: Components 0 and 1
            [2, 2, 2, 2],  # Row 2: Component 2 spans full width
        ],
        row_min_height="140px",
    ),
    components=[comp0, comp1, comp2],
)
```

**Grid Rules**:

- Each sub-list is a row
- Integers are component indices (0-based, consecutive)
- Use `-1` for empty cells
- Components span rectangular areas by repeating their index

### Optimal Grid Strategy

**8-Column Grid** (recommended for most dashboards):

```python
grid = [
    [0, 0, 1, 1, 2, 2, 3, 3],  # 4 KPI cards (2 cols each)
    [4, 4, 4, 5, 5, 5, 6, 6],  # 3 charts
    [4, 4, 4, 5, 5, 5, 6, 6],
    [4, 4, 4, 5, 5, 5, 6, 6],
    [7, 7, 7, 7, 7, 7, 7, 7],  # Full-width table
    [7, 7, 7, 7, 7, 7, 7, 7],
]
```

**12-Column Grid** (for finer control):

```python
grid = [
    [0, 0, 0, 1, 1, 1, 2, 2, 2, 3, 3, 3],  # 4 KPI cards (3 cols each)
    [4, 4, 4, 4, 5, 5, 5, 5, 6, 6, 6, 6],  # 3 charts (4 cols each)
    [4, 4, 4, 4, 5, 5, 5, 5, 6, 6, 6, 6],
    [4, 4, 4, 4, 5, 5, 5, 5, 6, 6, 6, 6],
]
```

### Component Sizing Guidelines

| Component   | Columns  | Rows | Min Height |
| ----------- | -------- | ---- | ---------- |
| KPI Card    | 2-3      | 1    | 140px      |
| Small Chart | 3-4      | 3    | 420px      |
| Large Chart | 4-6      | 4-5  | 560-700px  |
| Table       | 8 (full) | 4-6  | 560-840px  |

### Row Height Control

```python
# Always use 140px row height
vm.Grid(grid=[...], row_min_height="140px")

# Component height = row_min_height × rows_spanned
# KPI cards: 1 row = 140px (optimal)
# Charts: 3 rows = 420px (minimum for proper rendering)
# Tables: 4+ rows = 560px+ (adjust based on content)
```

### Creating Taller Components

Use list multiplication for components spanning multiple rows:

```python
grid = [
    [0, 0, 0, 0, 0, 0],  # Header: 1 row
    *[[1, 1, 1, 1, 1, 1]] * 3,  # Chart: 3 rows (repeat pattern)
    *[[2, 2, 2, 3, 3, 3]] * 4,  # Two charts side-by-side: 4 rows
]
```

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

### Template 1: KPIs + Chart + Table

```
+--+----------+------------------------------------------------------------------------+
|  |NAV       |                                                                        |
|  |          +------------------------------------------------------------------------+
|  |Page 1    |  +-------------+  +-------------+  +-------------+  +-------------+    |
|  |Page 2    |  | KPI 1       |  | KPI 2       |  | KPI 3       |  | KPI 4       |    |
|  |Page 3    |  +-------------+  +-------------+  +-------------+  +-------------+    |
|  |          |                                                                        |
|  |----------|  +----------------------------------+  +-----------------------------+  |
|  |FILTERS   |  |                                  |  |                             |  |
|  |          |  |  CHART: Primary Visualization    |  |  CHART: Secondary           |  |
|  |Date      |  |  [Bar chart]                     |  |  [Line chart]               |  |
|  |[v]       |  |                                  |  |                             |  |
|  |          |  +----------------------------------+  +-----------------------------+  |
|  |Region    |                                                                        |
|  |[v]       |  +---------------------------------------------------------------------+|
|  |          |  |                                                                     ||
|  |Category  |  |  TABLE: Detail Data                                                 ||
|  |[v]       |  |  [sortable, filterable]                                             ||
|  |          |  +---------------------------------------------------------------------+|
+--+----------+------------------------------------------------------------------------+
```

**Grid Pattern**:

```python
grid = [
    [0, 0, 1, 1, 2, 2, 3, 3],  # KPIs
    [4, 4, 4, 4, 5, 5, 5, 5],  # Charts
    [4, 4, 4, 4, 5, 5, 5, 5],
    [4, 4, 4, 4, 5, 5, 5, 5],
    [6, 6, 6, 6, 6, 6, 6, 6],  # Table
    [6, 6, 6, 6, 6, 6, 6, 6],
]
```

### Template 2: Full-Width Timeseries + Details

```
+--+----------+------------------------------------------------------------------------+
|  |NAV       |                                                                        |
|  |          +------------------------------------------------------------------------+
|  |Overview  |  +---------------------------------------------------------------------+|
|  |Details   |  |                                                                     ||
|  |          |  |  CHART: Revenue Trend [Timeseries Line - Full Width]                ||
|  |----------|  |  [hover: tooltip | click: drill to detail]                          ||
|  |FILTERS   |  +---------------------------------------------------------------------+|
|  |          |                                                                        |
|  |Year      |  CONTAINER: Regional Breakdown                                         |
|  |[v]       |  [Container Filters: Region v]                                         |
|  |          |  +------------------+  +------------------+  +------------------------+|
|  |Quarter   |  |                  |  |                  |  |                        ||
|  |[v]       |  |  CHART: By Region|  |  CHART: By Product| |  TABLE: Top Items      ||
|  |          |  |  [Bar chart]     |  |  [Pie chart]     |  |  [sortable]            ||
|  |          |  +------------------+  +------------------+  +------------------------+|
+--+----------+------------------------------------------------------------------------+
```

**Grid Pattern**:

```python
grid = [
    [0, 0, 0, 0, 0, 0, 0, 0],  # Full-width timeseries
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [1, 1, 1, 1, 1, 1, 1, 1],  # Container (full-width)
    [1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1],
]
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

| Scenario                  | Use Container?         |
| ------------------------- | ---------------------- |
| Group related charts      | Yes                    |
| Section needs own filters | Yes                    |
| Visual separation needed  | Yes                    |
| Simple sequential layout  | No (use Grid directly) |

### Container with Scoped Filters

```python
vm.Container(
    title="Regional Analysis",
    layout=vm.Grid(grid=[*[[0, 1]] * 3], row_min_height="140px"),  # 3 rows = 420px
    components=[
        vm.Graph(figure=px.bar(df, x="region", y="sales")),
        vm.Graph(figure=px.pie(df, values="sales", names="region")),
    ],
    controls=[
        vm.Filter(column="quarter"),  # Only affects this container
    ],
    variant="outlined",
)
```

### Container Styling

```python
# No visual styling (default)
vm.Container(variant="plain", ...)

# Background fill
vm.Container(variant="filled", ...)

# Border outline (recommended for major sections)
vm.Container(variant="outlined", ...)
```

## Filter and Parameter Placement

### Page-Level (Left Sidebar)

```python
vm.Page(
    title="Dashboard",
    components=[...],
    controls=[
        vm.Filter(column="date"),
        vm.Filter(column="region"),
        vm.Parameter(targets=["chart.metric"], selector=vm.Dropdown(...)),
    ],
)
```

### Container-Level

```python
vm.Container(
    title="Section",
    components=[...],
    controls=[
        vm.Filter(column="category"),  # Only affects this container
    ],
)
```

### Filter Type Selection

| Options Count | Recommended Selector  |
| ------------- | --------------------- |
| 2-3           | Radio buttons         |
| 4-7           | Dropdown              |
| 8+            | Dropdown with search  |
| Range         | Slider or RangeSlider |
| Date          | DatePicker            |

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

- **Primary metrics**: Larger cells (3-4 columns)
- **Secondary metrics**: Medium cells (2-3 columns)
- **Supporting details**: Smaller cells or tables

## Common Layout Mistakes

### 1. Charts Too Small

**Problem**: Charts crammed into 2×2 cells **Solution**: Minimum 3 columns × 3 rows for any chart

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

**Important**: Do not use emojis in dashboard implementations. Emojis in wireframes are for documentation only.

## Reference

- **Layouts**: https://vizro.readthedocs.io/en/latest/pages/user-guides/layouts/
- **Containers**: https://vizro.readthedocs.io/en/stable/pages/user-guides/container/
