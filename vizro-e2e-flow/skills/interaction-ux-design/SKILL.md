---
name: interaction-ux-design
description: Stage 2 of Vizro dashboard development. USE AFTER completing information-architecture. Designs how users navigate and explore data - determines layout logic, flow between overview and detail, placement of filters and controls, and creates wireframes. Must be completed before visual design.
---

# Interaction & UX Design for Vizro Dashboards

## Overview

Interaction Design translates the Information Architecture into user-friendly navigation and exploration patterns. This stage focuses on HOW users will interact with the dashboard, defining layouts, navigation flows, filter placement, and creating wireframes that serve as blueprints for implementation.

**Key Focus**: Decide how users navigate and explore data — the layout logic, flow between overview and detail, and placement of filters and controls.

## Process Workflow

### 1. Define Navigation Structure

**Three-tier navigation architecture** (Vizro standard):

```
Tier 1: Global Navigation
├── Multi-page sidebar (automatic in Vizro)
├── Page selection
└── Settings/preferences (theme toggle)

Tier 2: Page-level Controls
└── Page filters or parameters (left collapsible sidebar - Vizro requirement)

Tier 3: Component-level Interactions
├── Container-specific filters or parameters
├── Graph and table interactions (Cross-filter, Cross-parameter, or Cross-highlight in Vizro)
└── Export data
```

**Navigation patterns**:

**Progressive Disclosure**:
```
Overview (high-level KPIs)
    ↓ Click/Select
Detailed View (breakdown by dimension)
    ↓ Click/Select
Granular Analysis (individual records)
```

**Parallel Exploration**:
```
Tab 1: View A ←→ Tab 2: View B ←→ Tab 3: View C
(All tabs at same level, different perspectives)
```

**Deliverable**: Navigation flow diagram with all paths mapped.

### 2. Design Layout Grids

**Vizro Mandatory Structure**:
```
+--+------------+------------------------------------------------------------------------+
|  |NAV MENU    |                    MAIN CONTENT AREA                                   |
|  |            |                                                                        |
|  |------------|  [KPIs, Charts, Tables arranged here]                                  |
|  |FILTERS/    |                                                                        |
|  |PARAMS      |  CONTAINER: [Name]                                                     |
|  |(Page level)|  [Container Filters/Params] ← These appear IN the main area            |
|  |            |  [Container Components]                                                |
+--+------------+------------------------------------------------------------------------+
```

**Vizro layout principles**:
- ✅ **DO**: Place navigation + page level filters/params in left panel
- ✅ **DO**: Add container-level filters ABOVE container in main area
- ✅ **DO**: Use 2-3 charts maximum per row (side-by-side)
- ✅ **DO**: Keep KPI cards small (unless single critical metric)
- ✅ **DO**: Assign full width to tables with 6+ columns
- ✅ **DO**: Assign full width ONLY to timeseries line charts
- ✅ **DO**: Enable long pages (scroll) when 8+ components
- ✅ **DO**: Show interaction hints: [hover: tooltip], [click: drill-down]
- ❌ **DON'T**: Put filters in main area unless in a container
- ❌ **DON'T**: Create more than 3 columns of charts
- ❌ **DON'T**: Use full-width for non-timeseries charts
- ❌ **DON'T**: Use narrow tables when many columns exist
- ❌ **DON'T**: Force all content to fit without scrolling

**Chart aspect ratios**:
- Primary charts: 16:9 (wide format)
- Secondary charts: 4:3 (balanced)
- Gauges/Status: 1:1 (square)

**Full-width chart usage** (use sparingly):
- **ONLY for timeseries line charts** with continuous temporal data
- Example: Daily/hourly revenue trends, system performance over time
- Most charts should be arranged side-by-side (2-3 per row)

**Standard layout patterns**:

**Pattern 1: Executive Overview (Vizro Standard)**
```
+--+----------+------------------------------------------------------------------------+
|🏠|Dashboard |                                                                        |
|📊| v        +------------------------------------------------------------------------+
|📈|Overview  |  +------------+  +------------+  +------------+  +------------+        |
|📋|Detail    |  | Revenue    |  | Orders     |  | Customers  |  | Conversion |        |
|⚙️|Settings  |  | $1.2M ↗    |  | 8.5K ↗     |  | 2.3K ↘     |  | 3.2% →     |        |
|  |          |  +------------+  +------------+  +------------+  +------------+        |
|  |----------|                                                                        |
|  |FILTERS:  |  +---------------------------------------------------------------------+|
|  |          |  |                                                                     ||
|  |Date Range|  |  Revenue Trend Over Time [Timeseries Line Chart - Full Width]       ||
|  |[v]       |  |  [hover: tooltip | click: drill to daily view]                     ||
|  |          |  +---------------------------------------------------------------------+|
|  |          |  NOTE: Full-width only for timeseries line charts                     |
|  |Region    |                                                                        |
|  |☐ North   |  CONTAINER: Performance Breakdown                                      |
|  |☐ South   |  [Metric ▼] [Time Granularity ▼]                                      |
|  |☐ East    |  +---------------------------------+  +-------------------------------+|
|  |☐ West    |  |                                 |  |                               ||
|  |          |  |  By Region [Bar - 4:3]          |  |  By Category [Pie - 1:1]      ||
|  |Product   |  |  [click: filter page]           |  |  [click: drill-down]          ||
|  |Category  |  +---------------------------------+  +-------------------------------+|
|  |[v]       |                                                                        |
+--+----------+------------------------------------------------------------------------+
```
**Key features**: Left nav + page level filters (Date, Region, Category), Container has its own filters (Metric, Time Granularity), Interactive elements noted, **Full-width chart ONLY for timeseries line chart**

**Pattern 2: Analytics Deep-Dive (Multi-Container)**
```
+--+----------+------------------------------------------------------------------------+
|🏠|Analytics |                                                                        |
|📊| v        +------------------------------------------------------------------------+
|🔍|Explore   |  +------------------+  +------------------+  +-----------------------+  |
|📈|Trends    |  | Total Sales      |  | Avg Order Value  |  | Customer LTV          |  |
|📋|Reports   |  | [click: details] |  |                  |  |                       |  |
|  |          |  +------------------+  +------------------+  +-----------------------+  |
|  |----------|                                                                        |
|  |FILTERS:  |  CONTAINER: Main Analysis                                              |
|  |          |  [Comparison Period ▼] [Metric Type ▼]                                |
|  |Year      |  +---------------------------------+  +-------------------------------+|
|  |[2024 v]  |  |                                 |  |                               ||
|  |          |  |  Primary Trend [Combo - 16:9]   |  |  Secondary View [Bar - 16:9]  ||
|  |Quarter   |  |  [hover: compare periods]       |  |  [click: zoom range]          ||
|  |[v]       |  +---------------------------------+  +-------------------------------+|
|  |          |                                                                        |
|  |Business  |  CONTAINER: Distribution Analysis                                      |
|  |Unit      |  [Distribution Type ▼]                                                 |
|  |☐ Unit A  |  +---------------------------------+  +-------------------------------+|
|  |☐ Unit B  |  |                                 |  |                               ||
|  |☐ Unit C  |  |  Value Distribution             |  |  Frequency Analysis           ||
|  |          |  |  [Histogram - 4:3]              |  |  [Box Plot - 4:3]             ||
|  |Status    |  +---------------------------------+  +-------------------------------+|
|  |[v]       |                                                                        |
|  |          |  CONTAINER: Detailed Data                                              |
|  |          |  [Export ⬇] [Refresh ↻]                                               |
|  |          |  +---------------------------------------------------------------------+|
|  |          |  |  Transaction Details [AgGrid Table - Full Width]                    ||
|  |          |  |  [sortable | filterable | paginated]                                ||
|  |          |  +---------------------------------------------------------------------+|
+--+----------+------------------------------------------------------------------------+
```
**Key features**: Multiple containers, each with own filter set, Container-level actions (Export, Refresh), Full-width table with AgGrid features

**Pattern 3: Operational Monitoring (Real-time)**
```
+--+----------+------------------------------------------------------------------------+
|🏠|Monitor   |                                                                        |
|📊| v        +------------------------------------------------------------------------+
|🔴|Live      |  +---------+---------+---------+---------+---------------------------+  |
|📈|History   |  | 🟢 API  | 🟢 DB   | 🟡 Cache| 🔴 Queue| ⏰ Updated: 10:30:45    |  |
|⚙️|Config    |  | 99.9%   | 99.5%   | 95.2%   | ERROR   |                           |  |
|  |          |  +---------+---------+---------+---------+---------------------------+  |
|  |----------|                                                                        |
|  |PARAMS:   |  +---------------------------------+  +-------------------------------+|
|  |          |  |                                 |  |                               ||
|  |Refresh   |  |  CPU Usage [Line - 16:9]        |  |  Memory Usage [Line - 16:9]   ||
|  |Interval  |  |  [auto-refresh]                 |  |  [auto-refresh]               ||
|  |[30s v]   |  +---------------------------------+  +-------------------------------+|
|  |          |                                                                        |
|  |Time      |  CONTAINER: Service Health                                             |
|  |Window    |  [Service ▼] [Metric ▼]                                               |
|  |[1h v]    |  +------------------+  +------------------+  +-----------------------+  |
|  |          |  |                  |  |                  |  |                       |  |
|  |----------|  |  Current Load    |  |  Response Time   |  |  Error Rate           |  |
|  |FILTERS:  |  |  [Gauge - 1:1]   |  |  [Line - 4:3]    |  |  [Bar - 4:3]          |  |
|  |          |  +------------------+  +------------------+  +-----------------------+  |
|  |Service   |                                                                        |
|  |☐ API     |  CONTAINER: Recent Events                                              |
|  |☐ DB      |  [Severity ▼] [Limit: 100 ▼]                                          |
|  |☐ Cache   |  +---------------------------------------------------------------------+|
|  |☐ Queue   |  |  Event Log [AgGrid Table - Full Width]                              ||
|  |          |  |  [timestamp | service | severity | message]                         ||
|  |Severity  |  |  [auto-scroll to latest | color-coded rows]                         ||
|  |[v]       |  +---------------------------------------------------------------------+|
+--+----------+------------------------------------------------------------------------+
```
**Key features**: Parameters for refresh/time (left panel), Status indicators in KPI cards, Auto-refresh functionality, Color-coded table rows

**Pattern 4: Comparison Dashboard**
```
+--+----------+------------------------------------------------------------------------+
|🏠|Compare   |                                                                        |
|📊| v        +------------------------------------------------------------------------+
|📈|Period    |  CONTAINER: Key Metrics Comparison                                     |
|📋|Product   |  [Period A ▼] [Period B ▼] [vs Mode: YoY/MoM ▼]                      |
|🔍|Segment   |  +------------+  +------------+  +------------+  +-------------------+  |
|  |          |  | Period A   |  | Period B   |  | Change     |  | Indicator         |  |
|  |----------|  | $850K      |  | $920K      |  | +8.2% ↗    |  | 🟢 On Target      |  |
|  |FILTERS:  |  +------------+  +------------+  +------------+  +-------------------+  |
|  |          |                                                                        |
|  |Baseline  |  CONTAINER: Period Comparison                                          |
|  |Period    |  [View Type ▼]                                                         |
|  |[v]       |  +---------------------------------+  +-------------------------------+|
|  |          |  |                                 |  |                               ||
|  |Compare   |  |  Period A [Grouped Bar - 16:9]  |  |  Period B [Grouped Bar - 16:9]||
|  |Period    |  |  [hover: show values]           |  |  [click: drill to category]   ||
|  |[v]       |  +---------------------------------+  +-------------------------------+|
|  |          |                                                                        |
|  |Dimension |  CONTAINER: Category Breakdown                                         |
|  |          |  [Sort By ▼] [Top N: 10 ▼]                                            |
|  |Dimension |  +---------------------------------+  +-------------------------------+|
|  |☐ Product |  |                                 |  |                               ||
|  |☐ Region  |  |  Period A Breakdown             |  |  Period B Breakdown           ||
|  |☐ Channel |  |  [Treemap - 4:3]                |  |  [Treemap - 4:3]              ||
|  |          |  +---------------------------------+  +-------------------------------+|
|  |Metrics   |                                                                        |
|  |☐ Revenue |  CONTAINER: Variance Analysis                                          |
|  |☐ Volume  |  [Highlight: Top Movers ▼]                                            |
|  |☐ Margin  |  +---------------------------------------------------------------------+|
|  |          |  |  Detailed Variance Table [AgGrid - Full Width]                      ||
|  |          |  |  [sortable | colored by variance direction | export enabled]        ||
|  |          |  +---------------------------------------------------------------------+|
+--+----------+------------------------------------------------------------------------+
```
**Key features**: Period comparison controls, Variance visualization, Side-by-side breakdown views

**Pattern 5: Customer Analytics**
```
+--+----------+------------------------------------------------------------------------+
|🏠|Customers |                                                                        |
|📊| v        +------------------------------------------------------------------------+
|👥|Overview  |  +----------------+  +----------------+  +---------------------------+  |
|📈|Segments  |  | Total          |  | Active (30d)   |  | Churn Risk                |  |
|🎯|Cohorts   |  | 12,450         |  | 8,234 (66%)    |  | 342 (2.7%)                |  |
|💰|LTV       |  +----------------+  +----------------+  +---------------------------+  |
|  |          |                                                                        |
|  |----------|  CONTAINER: Customer Trends                                            |
|  |FILTERS:  |  [Metric ▼] [Granularity ▼] [Smoothing ▼]                            |
|  |          |  +---------------------------------+  +-------------------------------+|
|  |Cohort    |  |                                 |  |                               ||
|  |[v]       |  |  Customer Growth [Area - 16:9]  |  |  Retention [Line - 16:9]      ||
|  |          |  |  [hover: cohort details]        |  |  [click: segment view]        ||
|  |Segment   |  +---------------------------------+  +-------------------------------+|
|  |☐ Premium |                                                                        |
|  |☐ Standard|  CONTAINER: Segmentation Analysis                                      |
|  |☐ Basic   |  [Segment Dimension ▼] [Color By ▼]                                   |
|  |          |  +---------------------------------+  +-------------------------------+|
|  |Status    |  |                                 |  |                               ||
|  |☐ Active  |  |  Segment Distribution           |  |  RFM Scatter                  ||
|  |☐ At Risk |  |  [Donut - 1:1]                  |  |  [Scatter - 1:1]              ||
|  |☐ Churned |  |  [click: filter to segment]     |  |  [click: customer list]       ||
|  |          |  +---------------------------------+  +-------------------------------+|
|  |LTV Range |                                                                        |
|  |[v]       |  CONTAINER: Top Customers                                              |
|  |          |  [Rank By ▼] [Show: 20 ▼] [Actions: Export ⬇ | Contact 📧]         |
|  |Date      |  +---------------------------------------------------------------------+|
|  |Joined    |  |  Customer Details [AgGrid - Full Width]                             ||
|  |[v]       |  |  [ID | Name | Segment | LTV | Last Purchase | Status]              ||
|  |          |  |  [row selection enabled | bulk actions available]                  ||
|  |          |  +---------------------------------------------------------------------+|
+--+----------+------------------------------------------------------------------------+
```
**Key features**: Segmentation and cohort analysis, RFM scatter plot, Customer action buttons

**Pattern 6: Long-Form Report (Scroll-friendly)**
```
+--+----------+------------------------------------------------------------------------+
|🏠|Reports   |                                                                        |
|📊| v        +------------------------------------------------------------------------+
|📋|Executive |  HEADER: Q4 2024 Performance Report                                    |
|📈|Sales     |  [Export PDF ⬇] [Schedule 📅] [Share 🔗]                              |
|💼|Marketing |  +------------+  +------------+  +------------+  +-------------------+  |
|  |          |  | Revenue    |  | Growth     |  | Customers  |  | Satisfaction      |  |
|  |----------|  | $2.4M      |  | +12.3%     |  | 15.2K      |  | 4.5/5 ⭐          |  |
|  |FILTERS:  |  +------------+  +------------+  +------------+  +-------------------+  |
|  |          |                                                                        |
|  |Report    |  SECTION: Executive Summary                                            |
|  |Period    |  +---------------------------------------------------------------------+|
|  |[v]       |  |  [Text Block: Key highlights and strategic outcomes]               ||
|  |          |  +---------------------------------------------------------------------+|
|  |Business  |                                                                        |
|  |Unit      |  CONTAINER: Financial Performance                                      |
|  |[v]       |  [View ▼] [Compare to Budget ☐]                                       |
|  |          |  +---------------------------------+  +-------------------------------+|
|  |Include   |  |                                 |  |                               ||
|  |☐ Budget  |  |  Revenue Trend [Line - 16:9]    |  |  Profit Trend [Line - 16:9]   ||
|  |☐ Forecast|  +---------------------------------+  +-------------------------------+|
|  |☐ Previous|  +---------------------------------+  +-------------------------------+|
|  |  Year    |  |  By Business Unit [Bar - 4:3]   |  |  By Region [Map - 4:3]        ||
|  |          |  +---------------------------------+  +-------------------------------+|
|  |          |                                                                        |
|  |          |  CONTAINER: Operational Metrics                                        |
|  |          |  [Metric Group ▼]                                                      |
|  |          |  +---------------------------------+  +-------------------------------+|
|  |          |  |                                 |  |                               ||
|  |          |  |  KPI Progress vs Target         |  |  Completion Rate              ||
|  |          |  |  [Bullet Chart - 4:3]           |  |  [Gauge - 1:1]                ||
|  |          |  +---------------------------------+  +-------------------------------+|
|  |          |                    ⬇ SCROLL CONTINUES ⬇                               |
|  |          |  CONTAINER: Customer Analysis                                          |
|  |          |  [Segment ▼] [Show Details ☐]                                         |
|  |          |  +---------------------------------+  +-------------------------------+|
|  |          |  |                                 |  |                               ||
|  |          |  |  Acquisition [Area - 16:9]      |  |  Retention [Line - 16:9]      ||
|  |          |  +---------------------------------+  +-------------------------------+|
|  |          |  +---------------------------------------------------------------------+|
|  |          |  |  Customer Cohort Table [AgGrid - Full Width]                        ||
|  |          |  +---------------------------------------------------------------------+|
|  |          |                                                                        |
|  |          |  CONTAINER: Marketing Performance                                      |
|  |          |  [Channel ▼] [Campaign ▼]                                             |
|  |          |  +---------------------------------+  +-------------------------------+|
|  |          |  |  ROI by Channel [Bar - 4:3]     |  |  Conversion Funnel [4:3]      ||
|  |          |  +---------------------------------+  +-------------------------------+|
|  |          |                                                                        |
|  |          |  CONTAINER: Appendix                                                   |
|  |          |  +---------------------------------------------------------------------+|
|  |          |  |  Detailed Methodology and Data Sources [Text Block]                 ||
|  |          |  +---------------------------------------------------------------------+|
+--+----------+------------------------------------------------------------------------+
```
**Key features**: Multiple sections with scroll, Export/schedule actions, Appendix section for documentation

**Deliverable**: Layout templates for each page type.

### 3. Design Filter Strategy

**Vizro filter constraints**:
- Page-level filters: ONLY in left sidebar (collapsible)
- Container-level filters: Within component area
- Page level filters: Must be implemented as page-level on each page

**Filter placement decision tree**:
```
Is this filter needed across multiple visualizations?
├─ YES → Page-level filter (left sidebar)
│   └─ Affects all components on page
└─ NO → Container-level filter
    └─ Affects only specific component
```

**Filter types by use case**:

| Filter Type | Use Case | Placement | Example |
|------------|----------|-----------|---------|
| Date Range | Time period selection | Page-level | Last 30/60/90 days |
| Categorical | Segment selection | Page-level | Region, Product, Customer Type |
| Numerical | Range selection | Container-level | Price range, Score threshold |
| Search | Text matching | Page or Container | Customer name, Product ID |
| Multi-select | Multiple options | Page-level | Select multiple regions |

**Deliverable**: Filter specification document with placement and behavior.

### 4. Define Interaction Patterns

**Click interactions**:
- Single click: Select/highlight
- Double click: Drill-down
- Right click: Context menu (if applicable)

**Hover behaviors**:
- Show tooltip with details
- Highlight related data
- Display trend mini-chart

**Cross-filtering**:
```
User clicks on Chart A → Filters apply to Chart B, C, D
Example: Click "North Region" in map → All charts filter to North
```

**Drill-down paths**:
```
Level 1: Annual Summary
    ↓ Click on Q3
Level 2: Q3 Breakdown by Month
    ↓ Click on September
Level 3: September Daily Detail
    ↓ Click on Sept 15
Level 4: Hourly data for Sept 15
```

**Deliverable**: Interaction specification with all behaviors documented.

### 5. Create Wireframes

**Two-step wireframing process**:

**Step 1: ASCII Wireframes** (Rapid iteration)

Example for executive dashboard:
```


Legend: [F] = Filter  [▼] = Dropdown  [B] = Button
```

**Step 2: HTML Wireframe** (After approval)

Create simple HTML mockup with:
- Basic layout structure
- Placeholder components
- Interactive elements (non-functional)

**Deliverable**: ASCII wireframes for quick review, HTML wireframe for final approval.

## Vizro-Specific Constraints

**Must follow these Vizro patterns**:

1. **Page Navigation**: Automatic sidebar (left) for multi-page apps
2. **Page Filters**: MUST be in collapsible left sidebar
3. **Layouts**: Use Grid or Flex layout (no absolute positioning)
4. **Components**: Limited to Graph, Table, Card, Figure
5. **Containers**: Can use Tabs for organizing content
6. **Actions**: Export, filter, and parameter actions only
7. **Theme**: Light/dark toggle available by default

## Deliverables Checklist

### Required Outputs

1. **Navigation Flow Diagram**
   - All navigation paths
   - Breadcrumb structure
   - Back/forward behavior

2. **Layout Templates**
   - Grid specifications for each page type
   - Component placement rules

3. **Filter Specifications**
   - Complete list of filters
   - Placement (page vs container)
   - Default values and behaviors

4. **Interaction Matrix**

   | Component | Click | Hover | Drag | Keyboard |
   |-----------|-------|-------|------|----------|
   | Chart A   | ...   | ...   | ...  | ...      |
   | Table B   | ...   | ...   | ...  | ...      |

5. **Wireframes**
   - ASCII diagrams for all unique pages
   - HTML wireframe for primary pages
   - Annotations for interactions

6. **User Flow Documentation**
   - Step-by-step workflows
   - Decision points
   - Error states and edge cases

## Common UX Patterns

### Search-Filter-Analyze Pattern
```
1. Search/Filter (narrow dataset)
2. View Results (see matches)
3. Analyze (explore patterns)
4. Export/Act (take action)
```

### Overview-Detail Pattern
```
1. Overview (all data aggregated)
2. Filter (select subset)
3. Detail (examine specific items)
4. Context (return to overview)
```

### Compare-Contrast Pattern
```
1. Select Items (choose 2+ items)
2. Side-by-side View (see differences)
3. Highlight Differences (emphasize gaps)
4. Draw Conclusions (insights)
```

## Validation Checklist

Before proceeding to Visual Design:

- [ ] All user workflows are mapped and tested
- [ ] Navigation requires maximum 3 clicks to any information
- [ ] Filter placement follows Vizro constraints
- [ ] Layouts work on target screen sizes
- [ ] Wireframes approved by stakeholders
- [ ] Interaction patterns are consistent throughout
- [ ] Error states and empty states designed
- [ ] Loading states considered
- [ ] Accessibility requirements met (keyboard navigation)

## Next Steps

Once Interaction/UX Design is complete:

1. Proceed to **visual-data-design** skill for visual treatment
2. Share wireframes with development team
3. Create interactive prototype if needed
4. Document any technical constraints discovered

## Tips for Success

1. **Test early with paper prototypes** - Quick sketches reveal issues fast
2. **Follow platform conventions** - Use Vizro's standard patterns
3. **Design for the 80%** - Optimize for common use cases
4. **Progressive disclosure** - Don't show everything at once
5. **Consistent patterns** - Same action = same result everywhere
6. **Plan for errors** - Design helpful error states

## References for Further Reading

- Vizro Layout Documentation: https://vizro.readthedocs.io/en/stable/pages/user-guides/layouts/
- Vizro Navigation: https://vizro.readthedocs.io/en/stable/pages/user-guides/navigation/
- Vizro Filters: https://vizro.readthedocs.io/en/stable/pages/user-guides/filters/
- Vizro Actions: https://vizro.readthedocs.io/en/stable/pages/user-guides/actions/