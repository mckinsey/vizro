# Chart Selection Guide

## Chart Type Selection Matrix

### Comparison Charts

**Bar Chart (Horizontal/Vertical)**

- **Use for**: Comparing discrete categories or values
- **Best when**: 3-15 categories, significant differences between values
- **Avoid when**: Categories exceed 15, time-series data
- **Requirements**: Always start at zero baseline

**Column Chart**

- **Use for**: Comparing values across categories, especially time periods
- **Best when**: Showing discrete time periods (quarters, years)
- **Avoid when**: Too many data points (>12), continuous time series

**Grouped/Stacked Bar**

- **Use for**: Comparing subcategories within main categories
- **Best when**: Need to show part-to-whole and comparison simultaneously
- **Avoid when**: More than 5 subcategories, values are similar

### Trend and Time-Series Charts

**Line Chart**

- **Use for**: Showing trends over continuous time
- **Best when**: Many data points (15+), continuous data
- **Avoid when**: Comparing distinct categories, non-sequential data
- **Best practices**: Limit to 3-5 lines maximum, use distinct colors

**Area Chart**

- **Use for**: Showing cumulative trends, volume over time
- **Best when**: Emphasizing magnitude of change
- **Avoid when**: Multiple overlapping series (use stacked area instead)

**Sparkline**

- **Use for**: Showing micro-trends inline with text
- **Best when**: Limited space, general trend more important than exact values
- **Avoid when**: Precise values needed, multiple series

### Part-to-Whole Charts

**Pie Chart**

- **Use for**: Showing proportions of a whole
- **Best when**: 2-5 categories, one category >25%
- **Avoid when**: More than 5 categories, similar-sized slices, comparing multiple pies
- **Warning**: Often misused - consider bar chart alternative

**Donut Chart**

- **Use for**: Same as pie chart, but allows center annotation
- **Best when**: Need to display total value in center
- **Avoid when**: Same limitations as pie chart

**Stacked Bar (100%)**

- **Use for**: Comparing proportions across multiple groups
- **Best when**: Need to compare composition across categories
- **Avoid when**: Absolute values are more important than percentages

### Distribution Charts

**Histogram**

- **Use for**: Showing frequency distribution of continuous data
- **Best when**: Large datasets, understanding data distribution
- **Avoid when**: Categorical data, small sample sizes

**Box Plot**

- **Use for**: Showing statistical distribution (quartiles, outliers)
- **Best when**: Comparing distributions across groups
- **Avoid when**: Audience unfamiliar with statistical concepts

**Scatter Plot**

- **Use for**: Showing correlation between two variables
- **Best when**: Looking for patterns, relationships, clusters
- **Avoid when**: No relationship exists, too many overlapping points

### Specialized Charts

**Heatmap**

- **Use for**: Showing intensity across two dimensions
- **Best when**: Large datasets, pattern recognition
- **Avoid when**: Precise values needed, colorblind users without patterns

**Bullet Chart**

- **Use for**: Showing performance against targets
- **Best when**: Comparing actual vs target with context ranges
- **Avoid when**: No target/benchmark exists

**Waterfall Chart**

- **Use for**: Showing cumulative effect of sequential values
- **Best when**: Explaining how starting value becomes final value
- **Avoid when**: Non-sequential data, simple totals

## Chart Type Anti-Patterns

### Never Use

**3D Charts**

- Distort data perception
- Make values difficult to read
- Add no analytical value
- Exception: Legitimate 3D data visualization (very rare)

**Dual Y-Axis**

- Can manipulate perception
- Confusing for most users
- Alternative: Use separate charts or normalize scales

**Excessive Pie Charts**

- Human eyes poor at comparing angles
- Bar charts usually superior for comparison
- Limit to simple part-to-whole with few slices

### Use with Extreme Caution

**Radar/Spider Charts**

- Difficult to interpret
- Hard to compare values
- Alternative: Small multiples of bar charts

**Bubble Charts**

- Size differences hard to judge
- Overlapping bubbles problematic
- Alternative: Scatter with size legend or separate encoding

## Common Data-to-Chart Mismatches

| Data Type                 | Wrong Chart         | Right Chart  | Reason                                  |
| ------------------------- | ------------------- | ------------ | --------------------------------------- |
| Time series (many points) | Bar chart           | Line chart   | Bars for discrete, lines for continuous |
| Geographic data           | Column chart        | Map          | Spatial patterns lost in columns        |
| Decimal differences       | Pie chart           | Bar chart    | Angles imprecise for small differences  |
| Composition over time     | Multiple pie charts | Stacked area | Shows both composition and trend        |
| Comparison of 10+ items   | Pie chart           | Bar chart    | Too many slices unreadable              |
| Correlation               | Line chart          | Scatter plot | Line implies causation/sequence         |

## Chart Selection Decision Tree

1. **Comparing categories?**

    - Few categories (3-7) → Bar chart
    - Many categories (8-15) → Horizontal bar chart
    - With subcategories → Grouped/stacked bar

1. **Showing change over time?**

    - Few points (\<12) → Column chart
    - Many points (12+) → Line chart
    - Multiple series → Line chart (max 5 lines)

1. **Showing part-to-whole?**

    - Simple (2-5 parts) → Pie/donut chart
    - Complex or comparative → Stacked bar chart
    - Over time → Stacked area chart

1. **Showing distribution?**

    - Frequency → Histogram
    - Statistical summary → Box plot
    - Relationship → Scatter plot

1. **Showing performance?**

    - Against target → Bullet chart
    - Sequential changes → Waterfall chart
    - Across dimensions → Heatmap
