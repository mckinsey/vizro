---
name: visual-data-design
description: Stage 3 of Vizro dashboard development. USE AFTER completing interaction-ux-design. Translates wireframes into visually compelling and clear designs - selects appropriate chart types, establishes visual hierarchy, defines color strategy, and ensures data storytelling. Must be completed before development.
---

# Visual & Data Design for Vizro Dashboards

## Overview

Visual Design transforms wireframes into polished, professional dashboards that effectively communicate data insights. This stage focuses on chart selection, visual hierarchy, color strategy, typography, and ensuring clear data storytelling through thoughtful visual choices.

**Key Focus**: Translate analytical goals into clear and engaging visuals. Choose chart types, establish hierarchy, and apply consistent visual language.

## Process Workflow

### 1. Select Chart Types

**Chart selection decision tree**:

```
What am I trying to show?
│
├─ COMPARISON
│  ├─ Among items → Bar Chart (horizontal/vertical)
│  ├─ Over time → Line Chart (continuous) or Column Chart (discrete)
│  └─ Correlation → Scatter Plot
│
├─ COMPOSITION
│  ├─ Part-to-whole (static) → Pie/Donut (≤5 parts) or Stacked Bar
│  ├─ Part-to-whole (time) → Stacked Area or 100% Stacked Bar
│  └─ Components → Waterfall or Stacked Bar
│
├─ DISTRIBUTION
│  ├─ Single variable → Histogram or Box Plot
│  ├─ Two variables → Scatter Plot
│  └─ Three variables → Bubble Chart
│
├─ RELATIONSHIP
│  ├─ Two variables → Scatter Plot
│  ├─ Three variables → Bubble Chart
│  └─ Many variables → Heatmap or Parallel Coordinates
│
└─ TREND
   ├─ Over time → Line Chart
   ├─ With confidence → Line with confidence bands
   └─ Multiple series → Multi-line or Small Multiples
```

**Chart type guidelines**:

| Chart Type | Best For | Avoid When | Max Data Points |
|------------|----------|------------|-----------------|
| Line | Trends over time | < 5 data points | 100-200 per line |
| Bar | Comparing categories | > 20 categories | 10-15 bars |
| Pie/Donut | Part-to-whole (%) | > 5 slices | 5 slices max |
| Scatter | Correlation | < 20 points | 500-1000 |
| Heatmap | Patterns in matrix | < 5×5 grid | 50×50 |
| AgGrid | Exact values, sorting/filtering | Pattern finding | Unlimited (paginated) |
| Card/KPI | Single metric | Comparisons | 1 value |
| Map | Geographic data | Non-geographic | Depends on zoom |

**When to use Vizro custom charts**:

Use custom charts (with `@capture("graph")` decorator) when:
- You need post-update calls (`update_layout`, `update_xaxes`, `update_traces`)
- You need simple data manipulation (aggregation, filtering) right before visualization
- Standard `plotly.express` charts don't provide the required customization
- You want to add reference lines, annotations, or custom interactions
- You're creating complex visualizations with `plotly.graph_objects.Figure()`

Note: Custom chart implementation is covered in the **development-implementation** skill.

**Deliverable**: Chart type specification for each data visualization.

### 2. Establish Visual Hierarchy

**Hierarchy levels** (in order of emphasis):

```
Level 1: Primary Focus (Largest, boldest, top-left)
├─ Critical KPIs
├─ Alert states
└─ Primary message

Level 2: Secondary Information (Medium size, strong contrast)
├─ Supporting metrics
├─ Main visualizations
└─ Important filters

Level 3: Supporting Details (Smaller, moderate contrast)
├─ Context information
├─ Secondary charts
└─ Supplementary data

Level 4: Background Information (Smallest, low contrast)
├─ Metadata
├─ Timestamps
└─ Reference information
```

**Visual hierarchy techniques**:

1. **Size**: Larger = more important
2. **Color**: Bright/saturated = attention-grabbing
3. **Position**: Top-left = first viewed (F-pattern)
4. **Contrast**: High contrast = emphasis
5. **White space**: More space = more importance
6. **Typography**: Bold/larger = higher priority

**Example hierarchy application**:
```
┌─────────────────────────────────┐
│ PRIMARY KPI (72px, bold)        │  ← Level 1
│ $2.5M Revenue                   │
│ ↑ 12% (36px, green)             │  ← Level 2
├─────────────────────────────────┤
│ Trend Chart (main focus)        │  ← Level 2
│                                 │
├──────────┬──────────────────────┤
│ Secondary│ Details Table        │  ← Level 3
│ Metrics  │ (smaller font)       │
└──────────┴──────────────────────┘
Updated: 2:45 PM (12px, gray)        ← Level 4
```

**Deliverable**: Visual hierarchy guide with size, color, and position specs.

### 3. Define Color Strategy

**Vizro theme options**:
- `vizro_dark`
- `vizro_light`
- Both themes are colorblind-safe by default

**IMPORTANT: Use Vizro defaults for data visualizations**

Vizro provides automatic color palettes that work beautifully across light/dark themes. **Do NOT specify colors in standard charts** (scatter, line, bar, etc.) - let Vizro handle it automatically.

**Vizro core color palette** (use when colors must be specified):

```python
# Pick 2-3 colors from this list:
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
    "#52733e"   # Olive
]

# Use "gray" for neutral elements (backgrounds, borders, inactive states)
```

**Color usage guidelines**:

| Use Case | Color Choice | Example |
|----------|--------------|---------|
| Standard charts | Auto (no color specified) | Scatter, line, bar |
| Positive change | "#689f38" (green) | ↑ 12% profit |
| Negative change | "#ff5267" (pink/red) | ↓ 5% sales |
| Neutral/inactive | "gray" | Disabled state |
| Target/goal line | "gray" (dashed) | Budget line |
| Custom components | Pick from core palette | when necessary |

**Semantic color patterns**:
```python
# Success/positive
success_color = "#689f38"  # Green from core palette

# Warning/caution
warning_color = "#ff9222"  # Orange from core palette

# Error/negative
error_color = "#ff5267"   # Pink/red from core palette

# Neutral/inactive
neutral_color = "gray"
```

**Accessibility requirements**:
- Text contrast: Minimum 4.5:1 (WCAG AA)
- Large text: Minimum 3:1
- Interactive elements: Minimum 3:1
- Never use color alone to convey information
- Vizro default palettes are colorblind-safe

**Deliverable**: Color strategy document specifying when to use defaults vs. custom colors.

### 4. Design Typography System

**Vizro typography hierarchy**:

```
Dashboard Title: 24-28px, bold
Page Title: 20-24px, semibold
Section Header: 16-18px, semibold
Chart Title: 14-16px, medium
Body Text: 12-14px, regular
Labels: 10-12px, regular
Footnotes: 9-10px, regular
```

**Font recommendations**:
- Primary: System fonts (faster loading)
- Fallback stack: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif
- Monospace (for numbers): "SF Mono", Monaco, Consolas, "Courier New", monospace

**Number formatting**:
- Use consistent decimal places
- Add thousands separators (1,234,567)
- Use abbreviations for large numbers (1.2M, 3.4B)
- Align numbers right in tables
- Use monospace for better alignment

**Deliverable**: Typography specifications with sizes and weights.

### 5. Apply Data Storytelling Principles

**Visual narrative structure**:

```
1. Context (What's the situation?)
   └─ Reference lines, benchmarks, targets

2. Focus (What's important?)
   └─ Highlight key data points, use color/size

3. Insight (What does it mean?)
   └─ Annotations, callouts, trend indicators

4. Action (What should I do?)
   └─ Clear next steps, links to details
```

**Annotation guidelines**:
- Add context to unusual spikes/drops
- Label important thresholds
- Include data freshness indicators
- Provide calculation methods (hover/tooltip)

**Example annotated chart**:
```
Revenue Trend │
   $3M ──────│──────────────── Target
             │     ↓ Holiday spike
   $2M ──────│────/\──────────
             │   /  \
   $1M ──────│──/────\────────
             │ /      \
      └──────┴────────────────
         J F M A M J J A S O N D

   Note: 15% increase after campaign launch (May)
```

**Deliverable**: Data storytelling guidelines with annotation standards.

### 6. Create Visual Mockups

**Progression from wireframe to visual design**:

1. **Apply color palette** to wireframe elements
2. **Add real data** to replace placeholders
3. **Apply typography** system
4. **Include visual polish** (shadows, borders, icons)
5. **Add micro-interactions** specs (hover states)
6. **Create dark/light** theme versions

**Visual design checklist**:
```
□ Brand colors applied consistently
□ Visual hierarchy clear at a glance
□ Charts appropriate for data types
□ Text readable at target resolution
□ Sufficient color contrast (WCAG AA)
□ Consistent spacing (8px grid)
□ Icons meaningful and consistent
□ Loading states designed
□ Empty states designed
□ Error states designed
```

**Deliverable**: High-fidelity mockups for all pages.

## Vizro-Specific Visual Considerations

**Vizro built-in features**:
- Automatic theme switching (light/dark)
- Consistent component styling
- Responsive design built-in
- Colorblind-safe palettes
- Professional chart defaults

**Available Vizro Components**:

To see all available Vizro models for your installed version, run:

```bash
uv run python scripts/list_vizro_models.py
```

Or directly in Python:
```python
import vizro.models as vm
print(vm.__all__)
```

This will show components like: `Dashboard`, `Page`, `Graph`, `Figure`, `AgGrid`, `Container`, `Tabs`, `Filter`, `Parameter`, `Dropdown`, `Button`, and more.

**Common component categories**:
- **Layout**: `Dashboard`, `Page`, `Container`, `Tabs`, `Accordion`, `Grid`, `Flex`
- **Visualization**: `Graph`, `Figure`, `AgGrid`, `Card`, `Text`
- **Controls**: `Filter`, `Parameter`, `Dropdown`, `Checklist`, `RadioItems`, `Slider`, `RangeSlider`, `DatePicker`, `Switch`
- **Actions**: `Button`, `Action`, `Tooltip`

**Important**: Always use `vm.AgGrid` for tables (not `vm.Table` or `go.Table`). AgGrid provides better UX with sorting, filtering, and pagination.

**Layout strategies for proper spacing**:
- Use `vm.Flex()` for automatic spacing between components (simplest approach)
- Use `vm.Grid()` with `row_min_height` parameter (e.g., `row_min_height="500px"`) to control scroll behavior and prevent crowded components
- Combine approaches: Use Flex at page level, Grid inside containers for structured sections
- Recommended `row_min_height`: Set high enough so components can render properly without being crowded

**Customization options**:
- Custom CSS via `assets/` folder
- Theme configuration
- Chart styling via Plotly
- Custom color scales
- Logo and branding

## Deliverables Checklist

### Required Outputs

1. **Chart Specifications**
   ```
   Page: Sales Overview
   Component 1: Revenue Trend
   - Chart Type: Line chart
   - X-axis: Date (monthly)
   - Y-axis: Revenue ($)
   - Title: "Revenue Trend" (in vm.Graph, not plotly)
   - Color: Auto (use Vizro defaults)
   - Annotations: Q3 target line (gray, dashed)
   - Header/Footer: Optional context or source attribution
   ```

2. **Visual Hierarchy Guide**
   - Element sizes and weights
   - Reading order diagram
   - Emphasis techniques used

3. **Color Palette Document**
   - Primary, semantic, and data colors
   - Hex codes and RGB values
   - Usage guidelines
   - Accessibility notes

4. **Typography System**
   - Font stack
   - Size scale
   - Weight variations
   - Line height specs

5. **Visual Mockups**
   - High-fidelity designs
   - Interactive states

6. **Component Library**
   - Reusable visual elements
   - Chart templates
   - Icon set
   - Button styles

## Common Visual Patterns

### KPI Card Design

**Use Vizro built-in KPI cards** (`kpi_card` and `kpi_card_reference` from `vizro.figures`):

```
┌────────────────────────────┐
│ Title (14px, medium)       │
│ $1.2M (large, bold)        │
│ ↑ 15% vs last month (auto) │
│ [Icon] (optional)          │
└────────────────────────────┘
```

**Design considerations**:
- Title: Short metric name (2-4 words)
- Value: Formatted with `value_format` parameter
- Comparison: Automatic with `kpi_card_reference()` (green=positive, red=negative)
- Icon: Optional visual identifier
- Color: Automatic theme handling (use `reverse_color=True` when lower is better)

See `references/design_principles.md` for implementation details.

### Chart Title Pattern

**Important**: In Vizro, chart titles are specified in the `vm.Graph` component, NOT in the plotly code itself.

```python
# ✅ CORRECT - Title in vm.Graph
vm.Graph(
    figure=px.scatter(df, x="width", y="length", color="species"),
    title="Relationships between Sepal Width and Sepal Length",
    header="Additional context or description here",
    footer="SOURCE: **Data source, 2024**"
)

# ❌ WRONG - Don't put title in plotly code
vm.Graph(
    figure=px.scatter(df, x="width", y="length", title="Title here")  # Don't do this
)
```

**Visual structure**:
```
Title | Subtitle for context
[Visualization Area]
↓ Data as of: timestamp
```

### Alert Visual Treatment
```
⚠️ WARNING (amber background)
━━━━━━━━━━━━━━━━━━━━━━
Message text here
[Action Button]
```

## Validation Checklist

Before proceeding to Development:

- [ ] Visual design aligns with brand guidelines
- [ ] All charts appropriate for their data types
- [ ] Color usage is consistent and meaningful
- [ ] Text is readable at all sizes
- [ ] Contrast ratios meet WCAG AA standards
- [ ] Visual hierarchy guides eye movement correctly
- [ ] Data stories are clear without explanation
- [ ] Mockups approved by stakeholders
- [ ] Design works in both light/dark themes

## Next Steps

Once Visual Design is complete:

1. Proceed to **development-implementation** skill
2. Create design handoff documentation
3. Export assets (icons, images, logos)
4. Prepare style guide for developers

## Tips for Success

1. **Less is more** - Avoid chartjunk and decoration
2. **Consistency matters** - Same thing looks the same everywhere
3. **Data ink ratio** - Maximize data, minimize non-data ink
4. **Consider colorblindness** - 8% of men are colorblind
5. **Mobile first** - Design for smallest screen first
6. **Performance impacts** - Certain visuals slow dashboards (scatter with big data)

## Anti-Patterns to Avoid

### Never Do This:
- 3D charts (distort perception)
- Pie charts with >5 slices
- Dual Y-axes (confusing)
- Red/green only (colorblind issue)
- Truncated Y-axis (misleading)
- Decorative backgrounds (distraction)
- Too many colors (visual noise)
- Inconsistent scales (comparison issues)

## References

- Vizro Theming: https://vizro.readthedocs.io/en/stable/pages/user-guides/custom-themes/
- Plotly Styling: https://plotly.com/python/styling-plotly-express/
- Color Palettes: https://vizro.readthedocs.io/en/stable/pages/user-guides/custom-colors/
- WCAG Guidelines: https://www.w3.org/WAI/WCAG21/quickref/
