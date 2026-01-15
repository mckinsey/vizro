# Common Dashboard Mistakes

Anti-patterns to avoid, organized by dashboard development phase.

## Contents

- Phase 1: Requirements Mistakes (information overload, ignoring user workflow)
- Phase 2: Layout Mistakes (poor hierarchy, cluttered layout)
- Phase 3: Visualization Mistakes (wrong charts, color misuse, missing context)
- Phase 4: Implementation Mistakes (Vizro-specific issues)
- Quick Fixes Reference

---

## Phase 1: Requirements Mistakes

Mistakes in defining WHAT information to show and WHY.

### Information Overload

**Problem**:

- Too many metrics on single screen (>12 charts)
- Every available metric included
- No clear focus or priority
- Users cannot identify what matters

**Solution**:

- Follow "7 ± 2 rule": 5-9 key metrics maximum on main view
- Prioritize based on user goals
- Grouping related metrics into sections
- Create role-specific views
- Ask: "Does this help make a decision?"

### Ignoring User Workflow

**Problem**:

- Dashboard doesn't match user tasks
- Wrong metrics for user role
- No filtering options
- One-size-fits-all approach

**Solution**:

- Start with Phase 1 requirements gathering
- Create role-specific pages
- Allow filtering and customization
- Match metrics to decisions users make

### Non-Actionable Metrics

**Problem**: Metrics displayed but no action possible

**Solution**: Only show metrics that inform decisions; consider removing vanity metrics

### The "Hidden Value"

**Problem**: Most important info requires multiple clicks

**Solution**: Surface critical insights immediately on overview page

### The "Metric Graveyard"

**Problem**: Metrics no one looks at anymore

**Solution**: Regular audits; remove unused metrics

---

## Phase 2: Layout Mistakes

Mistakes in HOW users navigate and explore data.

### Poor Visual Hierarchy

**Problem**:

- All elements same size and weight
- Important metrics buried
- Random placement without logic
- No clear scanning path

**Solution**:

- Place critical KPIs top-left (F-pattern)
- Use size to indicate importance
- Group related metrics visually
- Create clear sections with spacing

**Visual Weight Guide**:

```
Primary metric: Large KPI card, prominent position
Secondary metric: Medium chart, supporting position
Tertiary metric: Smaller chart or table row
```

### Cluttered Layout

**Problem**:

- No white space
- Charts touching each other
- Dense, cramped feeling
- Difficult to distinguish sections

**Solution**:

- Use Grid layout with proper spacing
- Use containers to group related items
- Set appropriate `row_min_height`
- Leave visual breathing room

**Spacing Guidelines**:

```python
# Good: Charts span 3 rows (420px each)
vm.Grid(
    grid=[
        [0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1],
        [0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1],
        [0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1],
    ],
    row_min_height="140px",
)

# Bad: Charts only 1 row (140px - too small)
vm.Grid(grid=[[0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1]], row_min_height="140px")
```

### Inconsistent Time Ranges

**Problem**: Different charts showing different time periods

**Solution**: Use page-level date filter that affects all charts

### The "Surprise Me" Dashboard

**Problem**: Random order, no predictable structure

**Solution**: Consistent layout users can learn and memorize

---

## Phase 3: Visualization Mistakes

Mistakes in chart types, colors, and visual design.

### Inappropriate Chart Types

**Problem Examples**:

- Pie chart with 10+ slices
- Pie chart for time-series data
- 3D charts distorting values
- Line chart for categorical comparison
- Bar chart without zero baseline

**Solutions**:

| Wrong            | Right                 | Why                 |
| ---------------- | --------------------- | ------------------- |
| Pie (10 slices)  | Horizontal bar        | Readable            |
| Time-series pie  | Line/area chart       | Shows trend         |
| 3D bar chart     | 2D bar chart          | Accurate perception |
| Categorical line | Bar chart             | No false continuity |
| Truncated bars   | Zero baseline or line | Not misleading      |

### Color Misuse

**Problem**:

- Too many colors (>6)
- Similar shades hard to distinguish
- Inconsistent color meanings
- "Christmas tree" effect

**Solution**:

- Limit to 3 primary colors + neutrals
- Use color consistently (same entity = same color everywhere)
- Let Vizro handle colors automatically for most charts
- Reserve bright colors for highlights only

**Color Budget**:

```
Primary data: 1 color
Comparison: 1 contrasting color
Highlights/alerts: 1 accent color
Everything else: Grayscale
```

### Lack of Context

**Problem**:

- Numbers without comparison
- No date ranges shown
- Missing units or labels
- Unclear what "good" means

**Solution**:

- Always include comparisons (vs target, vs last period)
- Show date range prominently
- Include units in labels (%, $, units)
- Add reference lines for targets
- Show trends (up/down indicators)

**Context Template**:

```
[Metric Name]: [Value] [Unit]
[Time Period]
[Comparison]: [Direction] [Amount] vs [Reference]

Example: Revenue: $1.2M | Oct 2024 | +15% vs last month
```

### Inconsistent Design

**Problem**:

- Different chart styles across dashboard
- Varying font sizes and styles
- Inconsistent colors for same data
- Mixed labeling conventions

**Solution**:

- Use Vizro defaults (automatic consistency)
- Same color for same entity everywhere
- Consistent title format across charts
- Uniform tooltip format

### Truncated Y-Axis on Bar Charts

**Problem**: Bar charts not starting at zero exaggerate differences

**Solution**: Always start bar charts at zero; use line charts if truncation needed

### Too Many Decimal Places

**Problem**: `$1,234,567.89` or `45.3478%` creates cognitive load

**Solution**: Round appropriately

```python
# Good
value_format = "${value:,.0f}"  # $1,234,568
value_format = "{value:.1f}%"  # 45.3%

# Bad
value_format = "${value:,.2f}"  # $1,234,567.89
```

### Unclear Metric Names

**Problem**: "Conv Rate" or "ARPU" without explanation

**Solution**: Use full names or include header/footer for context

```python
vm.Graph(
    figure=px.bar(...),
    title="Conversion Rate",
    header="Percentage of visitors who made a purchase",
)
```

### Missing Legends

**Problem**: Colors without legend

**Solution**: Plotly includes legends by default; ensure they're visible

### Hidden Insights

**Problem**: Important findings buried in data

**Solution**: Surface key insights in KPI cards or chart titles

### The "Decorative Dashboard"

**Problem**: Pretty but not functional

**Solution**: Form follows function; beauty through clarity

---

## Phase 4: Implementation Mistakes

Vizro-specific coding mistakes.

### Chart Titles in Wrong Place

**Problem**: Putting title in plotly code instead of vm.Graph

```python
# WRONG - Title in plotly code
vm.Graph(figure=px.scatter(df, x="width", y="length", title="Title"))

# CORRECT - Title in vm.Graph
vm.Graph(
    figure=px.scatter(df, x="width", y="length", color="species"),
    title="Chart Title Here",
    header="Additional context",
    footer="SOURCE: **Data source**",
)
```

### Using go.Table Instead of AgGrid

**Problem**: Using `go.Table` or `vm.Table` for data tables

```python
# WRONG
vm.Graph(figure=go.Figure(go.Table(...)))

# CORRECT
from vizro.tables import dash_ag_grid

vm.AgGrid(figure=dash_ag_grid(df), title="Data Table")
```

### Specifying Colors Unnecessarily

**Problem**: Setting colors in standard charts when Vizro handles this automatically

```python
# WRONG - Unnecessary color specification
px.scatter(df, x="x", y="y", color_discrete_sequence=["red", "blue"])

# CORRECT - Let Vizro handle colors
px.scatter(df, x="x", y="y", color="category")
```

### No Empty States

**Problem**: Broken layout when no data available

**Solution**: Handle empty data gracefully in custom charts

