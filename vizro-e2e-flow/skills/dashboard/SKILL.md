---
name: dashboard
description: USE THIS SKILL FIRST when user wants to create and design a dashboard, ESPECIALLY Vizro dashboards. This skill enforces a 3-step workflow (requirements, layout, visualization) that must be followed before implementation. For implementation and testing, use the dashboard-builder skill after completing Steps 1-3.
---

# Building Vizro Dashboards

A structured workflow for creating effective dashboards with Vizro.

## How to Use This Skill

**CRITICAL**: Use this skill BEFORE implementation. After completing Steps 1-3, proceed to the dashboard-builder skill for implementation and testing.

**IMPORTANT**: Follow steps sequentially. Each step builds on the previous.

Copy this checklist and track your progress:

```
Dashboard Development Progress:
- [ ] Step 1: Understand Requirements (discuss with user, document decisions)
- [ ] Step 2: Design Layout & Interactions (wireframes, filter placement)
- [ ] Step 3: Select Visualizations (chart types, colors, KPIs)
- [ ] Next: Use dashboard-builder skill for implementation and testing
```

**Do not skip steps.** Handle partial context as follows:

- User has data but no requirements → Start at Step 1
- User has wireframes → Validate Step 1 decisions, then proceed from Step 2
- User asks to "just build it" → Explain value of steps, offer to streamline but not skip

**For simple dashboards** (single page, \<5 charts): Steps 1-3 can be abbreviated but not skipped entirely.

---

## Spec Files: Documenting Decisions

IMPORTANT: Each step produces a spec file in the `spec/` directory to document reasoning, enable collaboration, and allow resumption in future sessions. Create the `spec/` directory at project start.

Create the `spec/` directory at the start of the project.

---

## Step 1: Understand Requirements

**Goal**: Define WHAT information is presented and WHY it matters.

### Key Questions to Discuss

1. **Users**: Who uses this dashboard? What decisions do they make?
1. **Questions**: What are the 3-5 most important questions this answers?
1. **Data**: What sources are available? What's the refresh frequency?
1. **Structure**: How many pages? What's the logical grouping?

### Design Principles

- **Limit KPIs**: 5-7 primary metrics per page maximum
- **Clear hierarchy**: Overview → Detail → Granular (max 3 levels)
- **Persona-based**: Different users may need different views
- **Decision-focused**: Every metric should inform a decision

### REQUIRED OUTPUT: spec/1_information_architecture.yaml

Save this file BEFORE proceeding to Step 2:

```yaml
# spec/1_information_architecture.yaml
dashboard:
  name: [Name]
  purpose: [One sentence goal]
pages:
  - name: [Page Name]
    purpose: [What question does this answer?]
    kpis: [List of 3-7 key metrics]
data_sources:
  - name: [Source Name]
    type: [csv/database/api]
decisions:
  - decision: [What was decided]
    reasoning: [Why this choice was made]
```

### Validation Checklist

Before proceeding to Step 2:

- [ ] Every page has a clear, distinct purpose
- [ ] KPIs are measurable and actionable
- [ ] Data sources are accessible
- [ ] User has confirmed the structure

**Detailed guidance**: See [information_architecture.md](references/information_architecture.md); **Anti-patterns**: See [common_mistakes.md](references/common_mistakes.md) section "Step 1: Requirements Mistakes"

---

## Step 2: Design Layout & Interactions

**Goal**: Define HOW users navigate and explore data.

### Vizro Navigation Architecture

```
Tier 1: Global Navigation
├── Multi-page sidebar (automatic in Vizro)
└── Page selection

Tier 2: Page-level Controls
└── Filters/Parameters in left collapsible sidebar

Tier 3: Component-level
├── Container-specific filters/parameters
├── Cross-filter, cross-highlight interactions
└── Export actions
```

### Layout Strategy

**Optimal Grid Configuration**:

- Always use `row_min_height="140px"` (at page or container level)
- **12 columns recommended** (not enforced) - flexible due to many divisors (1, 2, 3, 4, 6, 12)
- Control height by giving components **more rows**

**Component Sizing** (based on 12-column grid, height = rows × 140px):

| Component   | Columns   | Rows | Height    |
| ----------- | --------- | ---- | --------- |
| KPI Card    | 3         | 1    | 140px     |
| Small Chart | 4         | 3    | 420px     |
| Large Chart | 6         | 4-5  | 560-700px |
| Table       | 12 (full) | 4-6  | 560-840px |

**Exceptions** - size based on content to render:

- Text-heavy Card → treat like a chart (3+ rows)
- Small Table (\<5 columns) → doesn't need full width
- Button → 1 row is enough

**Layout Rules**:

- Place 2-3 charts per row (side-by-side)
- Full-width ONLY for timeseries line charts
- Give charts minimum 3 rows (use `*[[...]] * 3` pattern)
- Use `-1` for intentional empty cells

### Filter Placement & Selectors

```
Filter needed across multiple visualizations?
├─ YES → Page-level (left sidebar)
└─ NO → Container-level (top of the container)
```

**Choose appropriate selectors** - don't default to Dropdown:

| Data Type     | Selector        | Example                  |
| ------------- | --------------- | ------------------------ |
| 2-4 options   | **RadioItems**  | Region (N/S/E/W)         |
| 5+ options    | Dropdown        | Category (many)          |
| Numeric range | **RangeSlider** | Price ($0-$1000)         |
| Single number | **Slider**      | Year (2020-2025)         |
| Date          | **DatePicker**  | Order date               |
| Multi-select  | **Checklist**   | Status (Active, Pending) |

### REQUIRED OUTPUT: spec/2_interaction_ux.yaml

Save this file BEFORE proceeding to Step 3:

```yaml
# spec/2_interaction_ux.yaml
pages:
  - name: [Must match Step 1]
    layout_type: grid  # or flex
    grid_columns: 12
    grid_pattern: [[0, 0, 0, 1, 1, 1, 2, 2, 2, 3, 3, 3]] # Component placement

    containers:
      - name: [Container Name]
        has_own_filters: true/false
    filter_placement:
      page_level: [columns with selector types]
      container_level: [columns with selector types]
wireframe: |
  [ASCII wireframe for ALL pages]
decisions:
  - decision: [What was decided]
    reasoning: [Why this choice was made]
```

### Validation Checklist

Before proceeding to Step 3:

- [ ] Layout follows Vizro constraints
- [ ] Filter placement is intentional and documented
- [ ] User has been presented ASCI wireframes for every page and approved them

**Wireframes & examples**: See [layout_patterns.md](references/layout_patterns.md); **Anti-patterns**: See [common_mistakes.md](references/common_mistakes.md) section "Step 2: Layout Mistakes"

---

## Step 3: Select Visualizations

**Goal**: Choose appropriate chart types and establish visual consistency.

### Chart Type Quick Reference

| Data Question           | Recommended Chart                   |
| ----------------------- | ----------------------------------- |
| Compare categories      | Bar chart (horizontal for 8+ items) |
| Show trend over time    | Line chart (12+ points)             |
| Part-to-whole (simple)  | Pie/donut (2-5 slices ONLY)         |
| Part-to-whole (complex) | Stacked bar chart                   |
| Distribution            | Histogram or box plot               |
| Correlation             | Scatter plot                        |

### Chart Anti-Patterns (Never Use)

- 3D charts, Pie charts with 6+ slices, Dual Y-axis, Bar charts not starting at zero

### Color Strategy

**Primary Rule**: Let Vizro handle colors automatically for standard charts.

**When to specify colors**:

- Semantic meaning (green=good, red=bad)
- Consistent entity coloring across charts
- Brand requirements

**Vizro Semantic Colors**:

```python
success_color = "#689f38"  # Green - positive
warning_color = "#ff9222"  # Orange - caution
error_color = "#ff5267"  # Pink/red - negative
neutral_color = "gray"  # Inactive
```

### KPI Card Pattern

Use `kpi_card()` for simple metrics, `kpi_card_reference()` for comparisons. Use `reverse_color=True` when lower is better (costs, errors). NEVER put `kpi_card` or `kpi_card_reference` as a custom chart, use the built-in `kpi_card` and `kpi_card_reference` in `Figure` model instead.

### Chart Title Pattern

**IMPORTANT**: Titles go in `vm.Graph(title=...)`, NOT in plotly code.

### REQUIRED OUTPUT: spec/3_visual_design.yaml

Save this file BEFORE proceeding to implementation (dashboard-builder skill):

```yaml
# spec/3_visual_design.yaml
visualizations:
  - name: [Chart Name]
    type: [bar/line/scatter/etc]
    needs_custom_implementation: true/false
    reason: [if custom: has_reference_line/needs_data_processing/etc]

color_decisions:
  - component: [Name]
    reason: [Why non-default color]
    colors: [List of hex codes]

kpi_cards:
  - name: [KPI Name]
    value_column: [column]
    format: [e.g., '${value:,.0f}']
    has_reference: true/false

decisions:
  - decision: [What was decided]
    reasoning: [Why this choice was made]
```

### Validation Checklist

Before proceeding to implementation (dashboard-builder skill):

- [ ] Chart types match data types (no pie charts for time series)
- [ ] No anti-patterns used
- [ ] Custom chart needs are identified
- [ ] Color usage is consistent and intentional

**Chart decision trees**: See [chart_selection.md](references/chart_selection.md); **Anti-patterns**: See [common_mistakes.md](references/common_mistakes.md) section "Step 3: Visualization Mistakes"



## Reference Files

| File                                                                  | When to Read                          |
| --------------------------------------------------------------------- | ------------------------------------- |
| [information_architecture.md](references/information_architecture.md) | Step 1: Deep dive on requirements    |
| [layout_patterns.md](references/layout_patterns.md)                   | Step 2: Wireframes, component sizing |
| [chart_selection.md](references/chart_selection.md)                   | Step 3: Chart decision trees         |
| [common_mistakes.md](references/common_mistakes.md)                   | All steps: Anti-patterns to avoid    |

---

## Quick Reference: Vizro Components

**Components**: `Dashboard`, `Page`, `Container`, `Tabs`, `Graph`, `Figure`, `AgGrid`, `Card`, `Filter`, `Parameter`, `Selector`, `Button`

**Key Imports**: `import vizro.models as vm`, `from vizro import Vizro`, `import vizro.plotly.express as px`, `from vizro.tables import dash_ag_grid`, `from vizro.figures import kpi_card, kpi_card_reference`, `from vizro.models.types import capture`
