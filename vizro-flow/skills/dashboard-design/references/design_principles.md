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

### Size and Emphasis

**Typography Hierarchy**

- Primary metrics: 32-48px bold
- Secondary metrics: 20-28px medium
- Labels: 12-16px regular
- Supporting text: 10-14px regular

**Visual Weight Distribution**

- Largest elements = most important
- Use size to create 3-4 distinct levels
- Consistent weight for similar importance

### White Space

**Critical for Readability**

- Minimum 16px between unrelated elements
- 24-32px between sections
- Generous padding around charts (16-24px minimum)
- Empty space guides eye and reduces cognitive load

## Color Strategy

### Color Palette Structure

**3-Color Maximum Rule**

- Primary color: Main brand/emphasis color
- Secondary color: Supporting/comparative data
- Accent color: Alerts, highlights, CTAs
- Neutrals: Grays for text, backgrounds, borders

**Sequential Color Scales**

- Use for continuous data (light to dark single hue)
- Minimum 3 steps, maximum 7 steps
- Ensure sufficient contrast between steps
- Example: Light blue → Medium blue → Dark blue

**Diverging Color Scales**

- Use for data with meaningful midpoint
- Two contrasting hues meeting at neutral
- Example: Red (negative) ← Gray (neutral) → Green (positive)

**Categorical Colors**

- Distinct hues for unrelated categories
- Maximum 6-8 distinct colors
- Use same color consistently for same entity across charts

### Color Accessibility

**Contrast Requirements**

- Text on background: Minimum 4.5:1 ratio (WCAG AA)
- Large text (18px+): Minimum 3:1 ratio
- Chart elements: Minimum 3:1 against background
- Interactive elements: 3:1 against adjacent colors

**Color Blindness Considerations**

- Never use color alone to convey information
- Supplement with patterns, icons, or labels
- Avoid red/green as sole differentiator
- Test with color blindness simulator
- Use tools: ColorOracle, Coblis, Adobe Color

**Semantic Color Usage**

- Red: Negative, error, critical, down
- Green: Positive, success, good, up
- Yellow/Orange: Warning, caution, moderate
- Blue: Neutral, informational, stable
- Gray: Inactive, disabled, background

## Typography

### Font Selection

**Sans-Serif for Dashboards**

- Better readability at small sizes
- Clean, modern appearance
- Examples: Inter, Roboto, Open Sans, Lato

**Font Pairing**

- Same font family with different weights (preferred)
- Maximum 2 font families total
- Distinct enough to create hierarchy

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

**Line Height and Spacing**

- Body text: 1.4-1.6 line height
- Labels: 1.2-1.3 line height
- Tight spacing for data tables: 1.1-1.2
- Letter spacing: -0.01em to 0.01em (subtle adjustments)

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

**Filter Behavior**

- Show applied filters prominently
- Allow easy clearing ("Clear all")
- Auto-apply or "Apply" button based on complexity
- Preserve state on navigation

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

**Content Structure**

```
[Metric Label]: [Value]
[Contextual Information]
[Comparison or Change] (optional)
```

**Example**:

```
Revenue: $1.2M
Oct 2024
↑ 15% vs last month
```

**Best Practices**

- Include metric name
- Add context (date, segment, etc.)
- Show change/comparison when relevant
- Max 3-4 lines of information

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

**Title Structure**

- Sentence case
- Action-oriented when possible ("Revenue increased 15%")
- Or descriptive ("Monthly Revenue Trend")
- No period at end

**Subtitle Usage**

- Additional context (date range, segment, notes)
- Smaller, lighter text
- Example: "Last 12 months | All regions"

## Performance and Loading

### Loading States

**Skeleton Screens**

- Show layout structure while loading
- Gray rectangles in place of charts
- Maintains visual hierarchy
- Better than spinners for perceived performance

**Progressive Loading**

- Load critical KPIs first
- Load below-fold charts on scroll
- Lazy load drill-down data
- Prioritize visible content

## Accessibility

### Screen Reader Support

**ARIA Labels**

- All interactive elements need labels
- Chart summaries in aria-label
- Data tables with proper headers
- Form fields with associated labels

**Example Chart Label**:

```html
aria-label="Line chart showing revenue trend from Jan to Dec 2024,
ranging from $1M to $1.5M, with an overall increase of 20%"
```

### Keyboard Navigation

**Requirements**

- All interactive elements focusable (tabindex)
- Visible focus indicators
- Logical tab order (left-to-right, top-to-bottom)
- Escape key closes modals/dropdowns
- Arrow keys for navigation within components

### Focus States

**Visual Indicators**

- 2-3px outline or border
- High contrast color (often blue)
- Clear but not overwhelming
- Never remove outlines without replacement

## Testing and Validation

### Usability Checklist

- [ ] Can users identify the most important metric in < 3 seconds?
- [ ] Is the purpose of the dashboard clear without explanation?
- [ ] Can users complete primary tasks in < 5 clicks?
- [ ] Are all charts appropriately sized (not too small)?
- [ ] Is the color usage consistent across all charts?
- [ ] Do all tooltips provide useful information?
- [ ] Have you tested with actual data (not lorem ipsum)?

### Accessibility Checklist

- [ ] All text meets contrast requirements (4.5:1 minimum)
- [ ] All interactive elements keyboard accessible
- [ ] Color is not the only means of conveying information
- [ ] All images and charts have appropriate alt text or ARIA labels
- [ ] Dashboard usable at 200% zoom
- [ ] Tested with screen reader (NVDA or JAWS)

### Performance Checklist

- [ ] Initial load time < 3 seconds
- [ ] Charts render smoothly (no jank)
- [ ] Filters apply in < 500ms
- [ ] Dashboard works with slow connections
- [ ] No memory leaks on long sessions
- [ ] Lazy loading implemented for below-fold content

## Advanced Considerations

### Data Density Management

Balance information and clarity:

- High density acceptable for expert users
- Low density for executive/casual users
- Use sparklines for inline trends
- Aggregate when >20 data points

### Real-Time Updates

Consider update frequency:

- Financial markets: Seconds
- Operational metrics: Minutes
- Business metrics: Hours/daily
- Strategic KPIs: Weekly/monthly

Match refresh rate to decision frequency.

### Error and Empty States

Design for edge cases:

- No data available: Helpful message + action
- Error loading: Clear error + retry option
- Filters return no results: Suggest alternatives
- Missing permissions: Explain limitation

Maintain layout integrity in all states.
