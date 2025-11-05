# Dashboard Wireframing Guide

## Purpose

Create low-fidelity dashboard wireframes using ASCII diagrams (for rapid iteration) and simple HTML (for stakeholder review). This guide focuses on what to create, not wireframing theory.

## Two-Step Wireframing Process

### Step 1: ASCII Diagram (Rapid Iteration)

**When to use**: Initial layout exploration, quick stakeholder feedback, multiple variations.

**What to create**: Text-based box diagram showing layout structure.

**ASCII Wireframe Template**:

```
+----------------------------------------------------------------------------------------+
| Dashboard Title                                                    [Filters] [Date]    |
+----------------------------------------------------------------------------------------+
|                                                                                        |
|  +---------------------------+  +------------------+  +------------------+             |
|  |                           |  |                  |  |                  |             |
|  |  PRIMARY KPI              |  |  KPI 2           |  |  KPI 3           |             |
|  |  $1.24M                   |  |  12,458          |  |  3.8%            |             |
|  |  ↑ 15.3% vs last period   |  |  ↑ 8.2%          |  |  ↓ 2.1%          |             |
|  |                           |  |                  |  |                  |             |
|  +---------------------------+  +------------------+  +------------------+             |
|                                                                                        |
|  +--------------------------------------------------------------------------------+    |
|  |                                                                                |    |
|  |  CHART: Revenue Trend                                                          |    |
|  |  [Line chart showing revenue over last 30 days]                                |    |
|  |                                                                                |    |
|  |                                                                                |    |
|  +--------------------------------------------------------------------------------+    |
|                                                                                        |
|  +--------------------------------------+  +--------------------------------------+    |
|  |                                      |  |                                      |    |
|  |  CHART: Revenue by Category          |  |  CHART: Traffic Sources              |    |
|  |  [Horizontal bar chart]              |  |  [Donut chart]                       |    |
|  |                                      |  |                                      |    |
|  +--------------------------------------+  +--------------------------------------+    |
|                                                                                        |
+----------------------------------------------------------------------------------------+
```

**Creation Guidelines**:

1. Use boxes made with `+`, `-`, `|` characters
2. Label all sections clearly: KPI, CHART, TABLE, FILTER, PARAMETER, ACTIONS, CONTAINER, TABS
3. Indicate chart types in brackets: `[Line chart]`, `[Bar chart]`
4. Show hierarchy through box sizes (larger = more important)
5. Include sample values for KPIs to show context
6. Keep it monospace-friendly
7. For Vizro: Consider FILTER vs PARAMETER (filters select data, parameters alter chart arguments), ACTIONS (exports, drill-throughs), CONTAINER/TABS for grouping

**Pattern Examples**:

**Executive Dashboard ASCII**:
```
+----------------------------------------------------------+
| Executive Dashboard           [Date: Last 30 days]       |
+----------------------------------------------------------+
|  +--------------+  +----------+  +----------+            |
|  | Revenue      |  | Users    |  | Conv %   |            |
|  | $1.24M ↑15%  |  | 12.5K ↑8%|  | 3.8% ↓2% |            |
|  +--------------+  +----------+  +----------+            |
|                                                          |
|  +----------------------------------------------------+  |
|  | Revenue Trend - Line Chart                         |  |
|  | [30 day trend]                                     |  |
|  +----------------------------------------------------+  |
+----------------------------------------------------------+
```

**Operational Dashboard ASCII**:
```
+----------------------------------------------------------+
| Operations Dashboard     [Live Updates] [Last 24h]       |
+----------------------------------------------------------+
| [ALERT: 2 issues detected]                               |
+----------------------------------------------------------+
|  +-----+  +-----+  +-----+  +-----+  +-----+  +-----+    |
|  | KPI |  | KPI |  | KPI |  | KPI |  | KPI |  | KPI |    |
|  +-----+  +-----+  +-----+  +-----+  +-----+  +-----+    |
|                                                          |
|  +----------------------------------------------------+  |
|  | Status Chart - Line with thresholds                |  |
|  +----------------------------------------------------+  |
|                                                          |
|  +----------------------------------------------------+  |
|  | Details Table - Recent Events                      |  |
|  +----------------------------------------------------+  |
+----------------------------------------------------------+
```

### Step 2: HTML Wireframe (Stakeholder Review)

**When to use**: After ASCII approval, for browser preview, stakeholder presentations.

**What to create**: Minimal HTML file with grayscale styling, grid layout, placeholders.

**HTML Wireframe Requirements**:

- **Grayscale only**: `#fff`, `#f5f5f5`, `#e5e5e5`, `#999`, `#333`
- **No branding**: Generic sans-serif font
- **Placeholders only**: Text like "[Line Chart]", "KPI: $1.24M"
- **Grid-based**: CSS Grid with clear structure
- **Minimal CSS**: <100 lines, inline styles okay
- **No JavaScript**: Static only
- **No real charts**: Gray boxes with labels

**HTML Wireframe Template**:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard Wireframe</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: #f5f5f5;
            padding: 20px;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            padding: 24px;
        }
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 24px;
            padding-bottom: 16px;
            border-bottom: 2px solid #e5e5e5;
        }
        .title { font-size: 24px; font-weight: 600; color: #333; }
        .filters { color: #666; font-size: 14px; }
        .grid {
            display: grid;
            grid-template-columns: repeat(12, 1fr);
            gap: 24px;
        }
        .card {
            background: white;
            border: 2px solid #e5e5e5;
            padding: 20px;
            display: flex;
            flex-direction: column;
        }
        .card-title {
            font-size: 12px;
            text-transform: uppercase;
            color: #999;
            margin-bottom: 12px;
        }
        .kpi-value { font-size: 36px; font-weight: 700; color: #333; }
        .kpi-change { font-size: 14px; color: #666; margin-top: 8px; }
        .placeholder {
            background: #e5e5e5;
            padding: 60px 20px;
            text-align: center;
            color: #999;
            border-radius: 4px;
            flex-grow: 1;
        }
        .span-4 { grid-column: span 4; }
        .span-3 { grid-column: span 3; }
        .span-6 { grid-column: span 6; }
        .span-8 { grid-column: span 8; }
        .span-12 { grid-column: span 12; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="title">Dashboard Title</div>
            <div class="filters">[Date Filter] [Region Filter]</div>
        </div>

        <div class="grid">
            <!-- Primary KPI -->
            <div class="card span-4">
                <div class="card-title">Revenue</div>
                <div class="kpi-value">$1.24M</div>
                <div class="kpi-change">↑ 15.3% vs last period</div>
            </div>

            <!-- Secondary KPIs -->
            <div class="card span-3">
                <div class="card-title">Active Users</div>
                <div class="kpi-value">12,458</div>
                <div class="kpi-change">↑ 8.2%</div>
            </div>

            <div class="card span-3">
                <div class="card-title">Conversion Rate</div>
                <div class="kpi-value">3.8%</div>
                <div class="kpi-change">↓ 2.1%</div>
            </div>

            <!-- Large Chart -->
            <div class="card span-12">
                <div class="card-title">Revenue Trend</div>
                <div class="placeholder">[Line Chart: Revenue over last 30 days]</div>
            </div>

            <!-- Two Medium Charts -->
            <div class="card span-6">
                <div class="card-title">Revenue by Category</div>
                <div class="placeholder">[Horizontal Bar Chart]</div>
            </div>

            <div class="card span-6">
                <div class="card-title">Traffic Sources</div>
                <div class="placeholder">[Donut Chart]</div>
            </div>
        </div>
    </div>
</body>
</html>
```

**Grid Span Reference**:
- `span-12`: Full width (main charts)
- `span-8`: Large (2/3 width)
- `span-6`: Medium (1/2 width)
- `span-4`: Primary KPI (1/3 width)
- `span-3`: Secondary KPI (1/4 width)

## Creating Wireframes: Workflow

### For Claude Code Users

1. **Understand requirements** (from design steps 1-2)
2. **Create ASCII diagram** first
   - Show to user inline in conversation
   - Iterate based on feedback
   - Create 2-3 variations if needed
3. **Generate HTML wireframe** after ASCII approval
   - Use template above
   - Adjust grid spans based on ASCII layout
   - Write to file (e.g., `wireframe.html`)
   - User can open in browser

### Common Layouts

**Grid Patterns for Different Designs**:

**Executive (focus on few large KPIs)**:
```
Row 1: [KPI span-4] [KPI span-3] [KPI span-3] [KPI span-2]
Row 2: [Chart span-12]
Row 3: [Chart span-6] [Chart span-6]
```

**Operational (many metrics, monitoring)**:
```
Row 1: [Alert span-12]
Row 2: [KPI span-2] [KPI span-2] [KPI span-2] [KPI span-2] [KPI span-2] [KPI span-2]
Row 3: [Chart span-8] [Status span-4]
Row 4: [Table span-12]
```

**Analytical (flexible exploration)**:
```
Row 1: [Filters span-12]
Row 2: [Primary Insight span-6] [Comparison span-6]
Row 3: [Chart span-4] [Chart span-4] [Chart span-4]
Row 4: [Table span-12]
```

## Quick Reference

### ASCII Wireframe Checklist
- [ ] Shows layout structure with boxes
- [ ] Labels all sections (KPI, CHART, TABLE, FILTER, PARAMETER, ACTIONS, CONTAINER, TABS)
- [ ] Indicates chart types in brackets
- [ ] Larger boxes = more important
- [ ] Monospace-friendly formatting
- [ ] Considers Vizro elements if targeting Vizro implementation

### HTML Wireframe Checklist
- [ ] Grayscale only (no colors)
- [ ] Grid-based layout with clear spans
- [ ] All charts as placeholder boxes
- [ ] Generic text (no real data)
- [ ] <100 lines of CSS
- [ ] Opens correctly in browser

### When to Show Each Type

| Need | Use ASCII | Use HTML |
|------|-----------|----------|
| Quick feedback | ✅ | ❌ |
| Multiple variations | ✅ | ❌ |
| Stakeholder review | ❌ | ✅ |
| Browser preview | ❌ | ✅ |
| Layout iteration | ✅ | ❌ |
| Final approval | ❌ | ✅ |

## Transition to Build

Once HTML wireframe is approved:
1. Proceed to **Step 9: Build Dashboard** in vizro-design skill
2. For Vizro: Use **vizro-implementation skill** for decision tree, MCP setup, and build guidance
3. Translate grid spans to Vizro Grid layout (component indices) or custom CSS
4. Replace placeholders with real components/charts
5. Apply styling (Vizro provides colorblind-safe default palette)

The wireframe structure becomes the implementation blueprint.

**Note**: Grid spans in HTML wireframe (span-12, span-6, etc.) map to Vizro Grid layout indices:
```python
layout=vm.Layout(grid=[[0, 1, 2], [3, 3, 3]])  # Component indices
```
