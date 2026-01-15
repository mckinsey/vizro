# Chart Selection Guide

Deep guidance for Phase 3: Selecting appropriate visualizations.

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
- Category labels are short (vertical) or long (horizontal)

**Avoid when**:

- Categories exceed 15 (consider grouping)
- Time-series data (use line chart)

**Requirements**: Always start Y-axis at zero

```python
# Vertical bar (short labels)
px.bar(df, x="category", y="value")

# Horizontal bar (long labels or many categories)
px.bar(df, x="value", y="category", orientation="h")
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
- Full-width layout recommended for timeseries

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
- Small sample sizes (\<30)

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
# See implementation_guide.md for examples
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

When colors must be specified (semantic meaning, brand, consistency):

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

### Semantic Color Usage

| Meaning           | Color    | Hex Code  |
| ----------------- | -------- | --------- |
| Positive/Success  | Green    | `#689f38` |
| Warning/Caution   | Orange   | `#ff9222` |
| Error/Negative    | Pink/Red | `#ff5267` |
| Neutral/Info      | Blue     | `#00b4ff` |
| Inactive/Disabled | Gray     | `gray`    |

### Color Palette Rules

**3-Color Maximum**:

- Primary: One Vizro core color
- Secondary: Complementary from core colors
- Accent: For emphasis
- Neutral: Gray for backgrounds/borders

**Sequential Scales** (continuous data):

- Light to dark single hue
- Derive from one Vizro core color
- 3-7 steps with sufficient contrast

**Diverging Scales** (data with midpoint):

- Two colors meeting at neutral
- Example: `#ff5267` (negative) ← gray → `#689f38` (positive)

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
