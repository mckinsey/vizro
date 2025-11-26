# Dashboard Design Principles

## Visual Hierarchy

### Layout Principles

**F-Pattern Priority**

- Place critical KPIs top-left (natural eye starting point)
- Secondary metrics top-right
- Supporting details below
- Least important information bottom-right

**Z-Pattern for Scanning**

- For sparse layouts: top-left → top-right → bottom-left → bottom-right
- Guide user through logical flow
- Use visual weight to enforce pattern

**Grid System**

- Use 12-column grid for flexibility
- Maintain consistent spacing (multiples of 8px)
- Align elements to grid for visual harmony
- Group related metrics within grid sections

### Vizro Layout Implementation

**Preventing crowded components** - three approaches:

**Option 1: Nested Layout Pattern**

- Use Flex at page level for vertically automatic flow
- Use Grid inside containers for structured sections
- Example: `vm.Page(layout=vm.Flex(), components=[vm.Graph(...), vm.Container(layout=vm.Grid(grid=[[0, 0, 1]]), components=[vm.Graph(...), vm.Graph(...)])])`
- Provides flexibility where needed, structure where required

**Option 2: Grid Layout with Row Height Control**

- Use `vm.Grid()` with `row_min_height` parameter for fine-grained control
- Example: `vm.Grid(grid=[[0, 1], [2, 2]], row_min_height="500px")`
- Provides precise control over component spacing and scroll behavior
- Best for: Complex layouts requiring structured arrangement
- IMPORTANT: Set `row_min_height` high enough so components can render properly

**Grid Configuration Details**:

- Grid provided as `list[list[int]]` where each sub-list is a row
- Integers correspond to component indices (must be consecutive starting from 0)
- Components span rectangular areas defined by their repeated index
- Use `*[[...]] * n` to repeat rows for taller components
- Example for varying heights:
    ```python
    vm.Grid(
        row_min_height="55px",
        grid=[
            [0, 0, 0, 0, 0, 0],  # Full-width header (1 row)
            *[[1, 1, 1, 1, 1, 1]] * 2,  # Full-width chart (2 rows)
            *[[2, 2, 2, 3, 3, 3]] * 5,  # Two components side-by-side (5 rows)
        ],
    )
    ```
- Actual component height = `row_min_height * rows_spanned`
- Larger grids (e.g., 6 or 12 columns) enable more precise positioning

**Option 3: Flex Layout (Automatic Spacing)**

- Use `vm.Flex()` at page level
- Automatically distributes components with proper spacing
- Best for: Extremely simple pages with sequential components
- No manual grid configuration needed
- Example: `vm.Page(title="Dashboard", layout=vm.Flex(), components=[...])`


**Reference**: https://vizro.readthedocs.io/en/latest/pages/user-guides/layouts/

### Container Visual Styling

Containers help visually distinguish sections and create clear information hierarchy:

**When to style containers**:

- Separate distinct content areas (e.g., metrics vs. analysis vs. data table)
- Emphasize important sections (e.g., alerts, key insights)
- Create visual breathing room between unrelated content
- Guide user attention through the page

**Visual styling options**:

- **variant parameter** for visual distinction:
  - `variant="plain"` (default): No visual styling, just logical grouping
  - `variant="filled"`: Background fill to emphasize sections
  - `variant="outlined"`: Border around container (recommended for major sections)
- **Titles**: Clear section headers to label grouped content

**Best practices**:

- Don't over-style (not every container needs visual distinction)

**Reference**: https://vizro.readthedocs.io/en/stable/pages/user-guides/container/#styled-containers

## Color Strategy

### Vizro Default Colors (Recommended)

**Primary approach: Let Vizro handle colors automatically**

Vizro provides built-in color palettes that are colorblind-accessible. **For standard charts (scatter, line, bar, pie, etc.), do NOT specify colors** - Vizro automatically applies appropriate colors.

**Vizro Core Color Palette** (when colors must be specified):

```python
vizro_colors = [
    "#00b4ff",  # Bright blue
    "#ff9222",  # Orange
    "#3949ab",  # Deep blue
    "#ff5267",  # Pink/red
    "#08bdba",  # Teal
    "#fdc935",  # Yellow
    "#689f38",  # Green
    "#976fd1",  # Purple
    "#f781bf",  # Light pink
    "#52733e",  # Olive
]
```

### When to Specify Colors

**Color selection guidelines**:

- Pick colors from the Vizro core palette above
- Or derive shades from 1core colors
- Use "gray" for neutral elements (backgrounds, borders, inactive states)
- Maintain consistency across dashboard

### Color Palette Structure

**3-Color Maximum Rule**

- Primary: Pick from Vizro core colors (e.g., "#00b4ff")
- Secondary: Pick complementary from core colors (e.g., "#ff9222")
- Accent: Pick for emphasis (e.g., "#ff5267")
- Neutral: Use "gray" for backgrounds, borders

**Sequential Color Scales**

- Use for continuous data (light to dark single hue)
- Derive from one Vizro core color
- Minimum 3 steps, maximum 7 steps
- Ensure sufficient contrast between steps

**Diverging Color Scales**

- Use for data with meaningful midpoint
- Two Vizro colors meeting at neutral
- Example: "#ff5267" (negative) ← "gray" (neutral) → "#689f38" (positive)

**Categorical Colors**

- Let Vizro handle automatically for standard charts
- If custom: pick from Vizro core palette
- Use same color consistently for same entity

### Color Accessibility

**Contrast Requirements**

- Text on background: Minimum 4.5:1 ratio (WCAG AA)
- Large text (18px+): Minimum 3:1 ratio
- Chart elements: Minimum 3:1 against background
- Interactive elements: 3:1 against adjacent colors

**Color Blindness Considerations**

- Never use color alone to convey information
- Supplement with patterns, icons, or labels
- Vizro default palettes are colorblind-safe

**Semantic Color Usage** (from Vizro core palette):

- Positive/success: "#689f38" (green)
- Warning/caution: "#ff9222" (orange)
- Error/negative: "#ff5267" (pink/red)
- Neutral/info: "#00b4ff" or "#3949ab" (blue)
- Inactive/disabled: "gray"

## Typography

### Text Formatting

**Number Formatting**

- Use thousand separators: 1,234,567
- Limit decimals: 0-2 places maximum
- Large numbers: Use K, M, B notation (1.2M)
- Currency: Symbol before number ($1.2M)
- Percentages: 1 decimal place (45.3%)

**Label Best Practices**

- Short and descriptive (2-5 words)
- Sentence case (not Title Case or UPPERCASE)
- No periods at end of labels
- Truncate with ellipsis if necessary (max 20 chars)

## Interaction Design

### Progressive Disclosure

**Three-Level Information Architecture**

1. **Overview Level**: 3-7 primary KPIs, high-level trends
1. **Detail Level**: Supporting metrics, comparative data (accessed via tabs or sections)
1. **Granular Level**: Individual records, deep analysis (accessed via drill-downs)

**Drill-Down Patterns**

- Click on chart → Filtered detail view
- Hover → Tooltip with exact values
- Click on metric → Time series or breakdown
- "Show more" → Expanded table or list

### Filters and Controls

**Filter Placement**

- **Global page filters: Left sidebar (recommended default)** - Always visible while scrolling, provides vertical space for 8-10+ filters, clear separation between controls and content. Collapsible to maximize chart space when not actively filtering. Consider alternative placements (top bar, top-right) only if there's a strong reason (e.g., 3-5 filters max, horizontal space at premium, executive dashboards with minimal filtering).
- Container filters: Above relevant container
- Chart-specific filters: Dropdown on chart header

**Filter Types**

- Date range: Date picker or preset ranges (Last 7/30/90 days)
- Single select: Dropdown (< 8 options) or radio buttons
- Multi-select: Dropdown with checkboxes (> 3 options)
- Search: For large lists (> 20 items)

### Parameters and Selectors

Parameters are selector components that modify visualization properties or switch between different views, without filtering the underlying data.

**Parameter Placement**

- Global page parameters: Left sidebar alongside filters (with visual separation via heading)
- Container parameters: Above relevant container

**Parameter Types**

- Chart type switching (bar → line → scatter)
- Metric selection (revenue vs profit vs growth rate)
- Aggregation level (daily → weekly → monthly)
- Visualization parameters (number of bins, color scheme, axis scales)
- View modes (table vs chart, stacked vs grouped)

**Parameter Behavior**

- Clearly distinguish from filters (use different visual treatment or section heading)
- Use dropdown for 2-5 options
- Use radio buttons or segmented control for binary/ternary choices
- Label clearly with what aspect is being controlled (e.g., "Chart Type:", "Show as:")
- Provide sensible defaults that work for most use cases

### KPI Cards

**Vizro Built-in KPI Cards**

Vizro provides two built-in KPI card functions:

- `kpi_card()`: Display a single metric value with optional formatting and icons
- `kpi_card_reference()`: Display a metric with comparison to reference value (shows delta and direction)

**Implementation**: Use `from vizro.figures import kpi_card, kpi_card_reference`

**Content Structure**

```
[Title/Metric Label]
[Value] with formatting
[Icon] (optional)
[Reference comparison] (for kpi_card_reference only)
```

**Design Considerations**

- **Title**: Short metric name (e.g., "Average Bill", "Revenue")
- **Value formatting**: Use `value_format` parameter (e.g., `"${value:.2f}"`, `"{value:.1f}%"`)
- **Icons**: Use `icon` parameter for visual identification (e.g., `"shopping_cart"`, `"trending_up"`). Use icons from Google Material Icons library.
- **Aggregation**: Specify `agg_func` if needed (e.g., `"sum"`, `"mean"`, `"median"`)
- **Reference comparison**: Use `kpi_card_reference()` to show change vs. baseline
- **Color direction**: Use `reverse_color=True` when lower is better (e.g., cost, error rate)

**Best Practices**

- Keep titles concise (2-4 words)
- Use consistent formatting across all KPI cards
- Choose appropriate aggregation function for the metric
- Use icons sparingly for key metrics only
- Use `kpi_card_reference()` when comparison is important
- Use Vizro's automatic color handling (green=positive, red=negative)
- Set `reverse_color=True` for metrics where decrease is positive

**Example Usage**:

```python
from vizro.figures import kpi_card, kpi_card_reference

# Simple KPI with value
kpi_card(data_frame=df, value_column="revenue", title="Total Revenue", value_format="${value:,.0f}")

# KPI with reference comparison
kpi_card_reference(
    data_frame=df,
    value_column="revenue",
    reference_column="previous_revenue",
    title="Revenue vs Last Month",
    value_format="${value:,.0f}",
    reference_format="{delta:+.1f}% vs last month",
)
```

**Reference**: https://vizro.readthedocs.io/en/latest/pages/user-guides/figure/#key-performance-indicator-kpi-cards

## Chart-Specific Guidelines

### Axes and Labels

**Y-Axis**

- Always start at zero for bar charts
- Can truncate for line charts if justified
- Show gridlines at major intervals only
- Label every other gridline if dense

**X-Axis**

- Horizontal labels preferred
- Rotate 45° only if necessary
- Skip labels if too dense (show every nth label)
- Ensure first and last labels visible

**Axis Titles**

- Include when unit ambiguous (%, $, units)
- Omit when obvious from context
- Position: Y-axis title rotated left, X-axis title below

### Gridlines and Reference Lines

**Gridlines**

- Light gray (#E0E0E0 or similar)
- Horizontal only for most charts
- Every other major tick for clarity
- Never emphasize grid over data

**Reference Lines**

- Use for targets, averages, benchmarks
- Distinct style (dashed, different color)
- Always label (e.g., "Target: 85%")
- Maximum 2-3 reference lines per chart

### Chart Titles and Subtitles

**Vizro Implementation**

In Vizro, chart titles are specified in the `vm.Graph` component, NOT in the plotly code:

```python
# ✅ CORRECT
vm.Graph(
    figure=px.scatter(iris, x="sepal_width", y="sepal_length", color="species"),
    title="Relationships between Sepal Width and Sepal Length",  # Title goes here
    header="Additional context or description",  # Optional header for more context
    footer="SOURCE: **Data source**",  # Optional footer for attribution
)

# ❌ WRONG - Don't put title in plotly code
vm.Graph(
    figure=px.scatter(iris, x="width", y="length", title="Title")  # Don't do this
)
```

**Title Structure**

- Sentence case
- Action-oriented when possible ("Revenue increased 15%")
- Or descriptive ("Monthly Revenue Trend")
- No period at end
- Specify in `vm.Graph(title=...)` parameter

**Additional Context with Header/Footer**

- `header`: Additional context, methodology, or description
- `footer`: Data source attribution or timestamps
- Both support markdown formatting
- Example: `footer="SOURCE: **Plotly iris data set, 2024**"`

## Testing and Validation

### Usability Checklist

- [ ] Can users identify the most important metric in < 3 seconds?
- [ ] Is the purpose of the dashboard clear without explanation?
- [ ] Can users complete primary tasks in < 5 clicks?
- [ ] Are all charts appropriately sized (not too small)?
- [ ] Is the color usage consistent across all charts?
- [ ] Do all tooltips provide useful information?

## Advanced Considerations

### Data Density Management

Balance information and clarity:

- High density acceptable for expert users
- Low density for executive/casual users
- Use sparklines for inline trends
- Aggregate when >20 data points
