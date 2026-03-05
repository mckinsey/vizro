# Chart Selection Guide

Deep guidance for Step 3: Selecting appropriate visualizations.

## Contents

- Chart Type Decision Tree (what are you showing?)
- COMPARISON Charts (bar, grouped bar)
- TREND Charts (line, area, column)
- COMPOSITION Charts (pie, stacked bar, stacked area)
- DISTRIBUTION Charts (histogram, box, violin)
- RELATIONSHIP Charts (scatter, bubble)
- PERFORMANCE Charts (bullet, waterfall)
- Specialized Charts (heatmap, treemap)
- Custom Charts (when and why to use custom charts)
- Color Strategy (Vizro palette, semantic colors, accessibility)
- Anti-Patterns to Avoid
- Quick Reference Table

## Chart Type Decision Tree

### 1. What Are You Showing?

```
What is your primary goal?
├── Comparing values → Go to COMPARISON
├── Showing change over time → Go to TREND
├── Showing parts of a whole → Go to COMPOSITION
├── Showing distribution → Go to DISTRIBUTION
├── Showing relationship → Go to RELATIONSHIP
└── Showing performance → Go to PERFORMANCE
```

## COMPARISON Charts

### Bar Chart (Horizontal/Vertical)

**Use for**: Comparing discrete categories or values

**Best when**:

- 3-15 categories
- Significant differences between values

**Prefer horizontal orientation (`orientation='h'`) by default** — horizontal bars prevent bars from appearing too wide and avoid crowded tick text on the axis.

**Avoid when**:

- Categories exceed 15 (consider grouping)
- Time-series data (use line chart)

**Requirements**: Always start Y-axis at zero

```python
# Horizontal bar (preferred default)
px.bar(df, x="value", y="category", orientation="h")

# Vertical bar (only for 4-6 categories with short labels)
px.bar(df, x="category", y="value")
```

### Grouped Bar Chart

**Use for**: Comparing subcategories within main categories

**Best when**:

- 2-4 subcategories per group
- Need to compare across groups

**Avoid when**:

- More than 5 subcategories (too cluttered)
- Values are very similar (hard to distinguish)

```python
px.bar(df, x="category", y="value", color="subcategory", barmode="group")
```

## TREND Charts

### Line Chart

**Use for**: Showing trends over continuous time

**Best when**:

- 12+ data points
- Continuous time series
- Comparing 2-5 series

**Avoid when**:

- Comparing distinct categories (use bar)
- Non-sequential data

**Best practices**:

- Limit to 3-5 lines maximum
- Use distinct colors
- Full-width layout recommended for time-series

```python
px.line(df, x="date", y="revenue", color="region")
```

### Area Chart

**Use for**: Showing cumulative trends, volume over time

**Best when**:

- Emphasizing magnitude of change
- Single series or stacked comparison

**Avoid when**:

- Multiple overlapping series (use stacked area or line)

```python
# Single series
px.area(df, x="date", y="volume")

# Stacked (composition over time)
px.area(df, x="date", y="value", color="category")
```

### Column Chart

**Use for**: Comparing values across discrete time periods

**Best when**:

- Fewer than 12 time periods
- Showing discrete intervals (Q1, Q2, etc.)

**Avoid when**:

- Continuous time with many points (use line)

```python
px.bar(df, x="quarter", y="revenue")
```

## COMPOSITION Charts

### Pie Chart / Donut Chart

**Use for**: Showing proportions of a whole

**Best when**:

- 2-5 categories ONLY
- One category is notably larger (>25%)
- Showing simple percentage breakdown

**Avoid when**:

- More than 5 categories
- Similar-sized slices
- Comparing multiple pies

**Warning**: Pie charts are often misused. Consider bar chart alternative.

```python
# Pie (2-5 categories only!)
px.pie(df, values="amount", names="category")

# Donut (shows total in center)
px.pie(df, values="amount", names="category", hole=0.4)
```

### Stacked Bar Chart

**Use for**: Comparing composition across multiple groups

**Best when**:

- Comparing how parts make up wholes across categories
- 2-5 segments per bar

```python
# Absolute values
px.bar(df, x="region", y="sales", color="product", barmode="stack")

# Percentages (100% stacked)
px.bar(df, x="region", y="sales", color="product", barmode="stack", barnorm="percent")
```

### Stacked Area Chart

**Use for**: Showing composition over time

**Best when**:

- Need to show both trend and composition
- 2-5 categories

```python
px.area(df, x="date", y="value", color="category")
```

## DISTRIBUTION Charts

### Histogram

**Use for**: Showing frequency distribution of continuous data

**Best when**:

- Large datasets (50+ values)
- Understanding data spread

**Avoid when**:

- Categorical data
- Small sample sizes (less than 30)

```python
px.histogram(df, x="value", nbins=20)
```

### Box Plot

**Use for**: Showing statistical distribution (quartiles, outliers)

**Best when**:

- Comparing distributions across groups
- Technical/analytical audience

**Avoid when**:

- Audience unfamiliar with box plots
- Need to show actual data points

```python
px.box(df, x="category", y="value")
```

### Violin Plot

**Use for**: Showing distribution shape with density

**Best when**:

- Need more detail than box plot
- Comparing distribution shapes

```python
px.violin(df, x="category", y="value")
```

## RELATIONSHIP Charts

### Scatter Plot

**Use for**: Showing correlation between two variables

**Best when**:

- Looking for patterns, relationships, clusters
- Two continuous variables

**Avoid when**:

- No relationship exists
- Too many overlapping points (use density plot)

```python
px.scatter(df, x="price", y="sales", color="category", size="quantity")
```

### Bubble Chart

**Use for**: Scatter with third variable encoded as size

**Use with caution**:

- Size differences hard to judge accurately
- Overlapping bubbles problematic

```python
px.scatter(df, x="x", y="y", size="z", color="category")
```

## PERFORMANCE Charts

### Bullet Chart

**Use for**: Showing performance against targets

**Best when**:

- Comparing actual vs target
- Including context ranges (poor/good/excellent)

```python
# Requires custom implementation with @capture("graph")
```

### Waterfall Chart

**Use for**: Showing cumulative effect of sequential values

**Best when**:

- Explaining how starting value becomes final value
- Financial breakdowns (revenue → costs → profit)

```python
import plotly.graph_objects as go
# Requires go.Waterfall for full control
```

## Specialized Charts

### Heatmap

**Use for**: Showing intensity across two dimensions

**Best when**:

- Large datasets
- Pattern recognition
- Correlation matrices

```python
px.density_heatmap(df, x="day", y="hour", z="value")
```

### Treemap

**Use for**: Hierarchical part-to-whole relationships

**Best when**:

- Nested categories
- Many categories (where pie fails)

```python
px.treemap(df, path=["region", "country", "city"], values="sales")
```

## Custom Charts

Standard `plotly.express` charts cover basic needs, but custom charts unlock more sophisticated visualizations that can tell a better story.

### When to Use Custom Charts

Use the `@capture("graph")` decorator when you need:

- **Post-update calls**: `update_layout()`, `update_xaxes()`, `update_traces()` to customize appearance
- **Reference lines or annotations**: Target lines, thresholds, trend lines
- **Data manipulation**: Calculations or transformations before visualization
- **Advanced chart types**: Waterfall, bullet charts, or multi-trace `go.Figure()` compositions
- **Custom styling**: Specific formatting not available in `px` defaults

### What Custom Charts Enable

Custom charts are powerful. They let you:

- Add horizontal/vertical reference lines showing targets or benchmarks
- Create multi-layered visualizations combining different trace types
- Apply conditional formatting based on data values
- Build chart types not available in `plotly.express`
- Customize every aspect of the visualization

## Color Strategy

### Default Approach: Let Vizro Handle Colors

**Primary rule**: For standard charts, do NOT specify colors. Vizro automatically applies colorblind-accessible palettes.

### Vizro Core Color Palette

When colors must be specified (semantic meaning, brand, consistency), use `vizro.themes`:

```python
from vizro.themes import colors, palettes

# Access individual colors
colors.blue  # "#097DFE"
colors.dark_purple  # "#6F39E3"
colors.turquoise  # "#05D0F0"
colors.dark_green  # "#0F766E"
colors.light_purple  # "#8C8DE9"
colors.light_green  # "#11B883"
colors.light_pink  # "#E77EC2"
colors.dark_pink  # "#C84189"
colors.yellow  # "#C0CA33"
colors.gray  # "#3E495B"

# Access full palettes
palettes.qualitative  # 10-color categorical palette (colors above)
palettes.sequential_blue  # Sequential blue scale (9 steps)
palettes.sequential_green  # Sequential green scale (9 steps)
palettes.sequential_pink  # Sequential pink scale (9 steps)
palettes.diverging  # Diverging pink-to-blue scale
```

### Semantic Color Usage

These colors are **separate from the chart palette** and intentionally bold. Use them ONLY for status indicators, notifications, KPI highlights, and error states — NOT in charts or data visualizations where they would be too visually aggressive.

| Meaning           | Color  | Hex Code  |
| ----------------- | ------ | --------- |
| Positive/Success  | Green  | `#26BF56` |
| Warning/Caution   | Orange | `#FFC107` |
| Error/Negative    | Red    | `#E84A3A` |
| Neutral/Info      | Blue   | `#097DFE` |
| Inactive/Disabled | Gray   | `gray`    |

### Color Palette Rules

**3-Color Maximum**:

- Primary: One Vizro core color
- Secondary: Complementary from core colors
- Accent: For emphasis
- Neutral: Gray for backgrounds/borders

**Sequential Scales** (continuous data):

- Use built-in palettes: `palettes.sequential_blue`, `palettes.sequential_green`, `palettes.sequential_pink`, `palettes.sequential_purple`, `palettes.sequential_turquoise`, `palettes.sequential_yellow`, `palettes.sequential_gray`
- Pass via `color_continuous_scale` parameter
- `palettes.sequential` is an alias for `palettes.sequential_blue`

**Diverging Scales** (data with midpoint):

- Use `palettes.diverging` (pink-to-blue via gray midpoint)
- Pass via `color_continuous_scale` with `color_continuous_midpoint=0`

### Color Accessibility

**Contrast Requirements**:

- Text on background: Minimum 4.5:1 (WCAG AA)
- Large text (18px+): Minimum 3:1
- Chart elements: Minimum 3:1 against background

**Color Blindness**:

- Never use color alone to convey information
- Supplement with patterns, icons, or labels
- Vizro default palettes are colorblind-safe

## Anti-Patterns to Avoid

### Never Use

| Chart Type      | Problem                 | Alternative     |
| --------------- | ----------------------- | --------------- |
| 3D Charts       | Distort perception      | 2D equivalent   |
| Dual Y-Axis     | Confusing, manipulative | Separate charts |
| Pie (6+ slices) | Unreadable              | Bar chart       |
| Radar/Spider    | Hard to interpret       | Small multiples |

### Use with Caution

| Chart Type   | Risk                     | Mitigation           |
| ------------ | ------------------------ | -------------------- |
| Bubble       | Size hard to compare     | Add size legend      |
| Stacked Area | Overlapping trends       | Limit to 4 series    |
| Gauge        | Takes space, little info | Use KPI card instead |

## Quick Reference Table

| Data Type                 | Wrong Chart   | Right Chart  | Why                       |
| ------------------------- | ------------- | ------------ | ------------------------- |
| Time series (many points) | Bar           | Line         | Lines show continuity     |
| Geographic                | Bar           | Map          | Spatial patterns visible  |
| Small differences         | Pie           | Bar          | Bars more precise         |
| Composition over time     | Multiple pies | Stacked area | Shows trend + composition |
| 10+ categories            | Pie           | Bar          | Readable labels           |
| Correlation               | Line          | Scatter      | Line implies sequence     |
