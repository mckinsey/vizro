# Common Dashboard Mistakes

Anti-patterns to avoid, organized by dashboard development step.

## Contents

- Step 1: Requirements Mistakes (information overload, ignoring user workflow)
- Step 2: Layout & Interaction Mistakes (poor hierarchy, cluttered layout, over-using interactions, missing affordances, drill-through gotchas)
- Step 3: Visualization Mistakes (wrong charts, color misuse, missing context)
- Quick Fixes Reference

---

## Step 1: Requirements Mistakes

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

- Start with Step 1 requirements gathering
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

## Step 2: Layout & Interaction Mistakes

Mistakes in HOW users navigate and explore data. The first group is about static layout (hierarchy, spacing, structure). The second group is about advanced interactions (cross-filter, cross-highlight, drill-through) — see the **wiring-vizro-actions** skill for the 6 named patterns those mistakes reference.

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

**Spacing rule**: Give every chart at least 3 rows in the grid (420px at `row_min_height="140px"`). A chart in a single row (~140px) will look squeezed and unreadable. See the **designing-vizro-layouts** skill for the full component sizing table.

### Inconsistent Time Ranges

**Problem**: Different charts showing different time periods

**Solution**: Use page-level date filter that affects all charts

### The "Surprise Me" Dashboard

**Problem**: Random order, no predictable structure

**Solution**: Consistent layout users can learn and memorize

### Over-using Interactions

**Problem**: 3+ cross-filters on one page — users lose track of what affects what.

**Solution**: Limit to 1–2 interaction patterns per page. Match each interaction to a named pattern from the **wiring-vizro-actions** skill; if you cannot name the pattern, the interaction probably isn't justified.

### Feature-First Thinking

**Problem**: "Let's add cross-filter because we can" without a clear user need.

**Solution**: Start from user task. What decision does this interaction enable? If a standard sidebar filter covers it, don't add a click-driven cross-filter.

### Cross-Filter When a Filter Suffices

**Problem**: Adding cross-filter for fewer than ~5 groups, where a dropdown would be just as fast.

**Solution**: Cross-filter pays off when the data has hierarchy (Pattern 1 / 2) or when click-to-explore is more natural than dropdown selection. Otherwise prefer the sidebar filter.

### No Visual Affordance on Interactive Source

**Problem**: User has no idea a chart or table is clickable.

**Solution**: Add a short, action-oriented `header` on every Graph/AgGrid with `actions=` (e.g. `header="Click a bar to filter by region"`). Avoid verbose or vague hints.

### Missing Back Button on Drill-Through Target

**Problem**: User navigates to a detail page (Pattern 1) and feels trapped.

**Solution**: The drill-through target page MUST include a back `vm.Button(text="← Back", href="/source-page", variant="outlined")` as the first component. The page MUST also use `layout=vm.Flex(direction="column")` so the button takes natural height — Grid would waste a 140px+ row.

### Missing `show_in_url=True` for Cross-Page

**Problem**: Cross-page drill-through silently fails — no error, just no filtering on the target page.

**Solution**: The Filter on the target page must have `show_in_url=True`.

### Cross-Filter When You Wanted to Highlight

**Problem**: Click filters data out, removing comparison context — but the user just wanted to emphasize one entity.

**Solution**: Use Pattern 3 (Comparison Spotlight) — Parameter targeting a custom chart's `highlight_X` argument, `visible=False`, `"NONE"` in selector options. The data stays, only the styling changes.

### Self-Highlight Without Visual Contrast

**Problem**: Clicked bar/point looks identical to the others — no feedback.

**Solution**: The custom chart must clearly differentiate highlighted vs non-highlighted (opacity, color, line width, marker border). See the **wiring-vizro-actions** skill's Pattern 3 / 5 and `custom_charts_guide.md` ("Highlight-Aware Custom Charts").

### Invisible Interactions With No Reset Path

**Problem**: Highlight or filter is active but the user can't tell, and there is no obvious way back.

**Solution**: Keep controls visible where possible. For `visible=False` highlight Parameters, include `"NONE"` in the selector options and rely on Vizro's built-in "Reset controls" button to clear state.

### Using Deprecated `filter_interaction`

**Problem**: `filter_interaction` is deprecated and produces warnings or unexpected behavior.

**Solution**: Use `va.set_control` instead.

---

## Step 3: Visualization Mistakes

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

- Let Vizro handle colors automatically unless the user asked otherwise (see **selecting-vizro-charts** and dashboard-design Step 3).
- When the user **has** requested custom colors: limit to a small palette, use color consistently (same entity = same color everywhere), and reserve bright colors for highlights only.

**Color budget** (only after the user asked for custom colors):

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

### Custom charts as KPI cards

**Problem**: Model rebuilds KPI cards as custom charts instead of using built-in functions.

**Solution**: Use built-in `kpi_card` / `kpi_card_reference` only; do data manipulation in `app.py`. See **selecting-vizro-charts** skill.
