---
name: dashboard
description: USE THIS SKILL FIRST when user wants to create, design, or build a dashboard. Do NOT jump to MCP tools directly - this skill enforces a 5-phase workflow (requirements, layout, visualization, implementation, testing) that must be followed. MCP tools like vizro-mcp are only used in Phase 4 after completing Phases 1-3 with the user.
---

# Building Vizro Dashboards

A structured workflow for creating effective dashboards with Vizro.

## How to Use This Skill

**CRITICAL**: Use this skill BEFORE any MCP tools. The vizro-mcp tools are only for Phase 4 (Implementation) after you have completed Phases 1-3 with the user.

**IMPORTANT**: Follow phases sequentially. Each phase builds on the previous.

Copy this checklist and track your progress:

```
Dashboard Development Progress:
- [ ] Phase 1: Understand Requirements (discuss with user, document decisions)
- [ ] Phase 2: Design Layout & Interactions (wireframes, filter placement)
- [ ] Phase 3: Select Visualizations (chart types, colors, KPIs)
- [ ] Phase 4: Implement Dashboard (MCP tools or Python code)
- [ ] Phase 5: Test & Verify (launch, navigation, controls)
```

**Do not skip phases.** Handle partial context as follows:

- User has data but no requirements → Start at Phase 1
- User has wireframes → Validate Phase 1 decisions, then proceed from Phase 2
- User asks to "just build it" → Explain value of phases, offer to streamline but not skip

**For simple dashboards** (single page, \<5 charts): Phases 1-3 can be abbreviated but not skipped entirely.

---

## Spec Files: Documenting Decisions

IMPORTANT: Each phase produces a spec file in the `spec/` directory to document reasoning, enable collaboration, and allow resumption in future sessions. Create the `spec/` directory at project start.

Create the `spec/` directory at the start of the project.

---

## Phase 1: Understand Requirements

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

Save this file BEFORE proceeding to Phase 2:

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

Before proceeding to Phase 2:

- [ ] Every page has a clear, distinct purpose
- [ ] KPIs are measurable and actionable
- [ ] Data sources are accessible
- [ ] User has confirmed the structure

→ See `references/information_architecture.md` for detailed guidance
→ See `references/common_mistakes.md` section: Phase 1: Requirements Mistakes

---

## Phase 2: Design Layout & Interactions

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
- Small Table (<5 columns) → doesn't need full width
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

| Data Type      | Selector        | Example                    |
| -------------- | --------------- | -------------------------- |
| 2-4 options    | **RadioItems**  | Region (N/S/E/W)           |
| 5+ options     | Dropdown        | Category (many)            |
| Numeric range  | **RangeSlider** | Price ($0-$1000)           |
| Single number  | **Slider**      | Year (2020-2025)           |
| Date           | **DatePicker**  | Order date                 |
| Multi-select   | **Checklist**   | Status (Active, Pending)   |

### REQUIRED OUTPUT: spec/2_interaction_ux.yaml

Save this file BEFORE proceeding to Phase 3:

```yaml
# spec/2_interaction_ux.yaml
pages:
  - name: [Must match Phase 1]
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

Before proceeding to Phase 3:

- [ ] Layout follows Vizro constraints
- [ ] Filter placement is intentional and documented
- [ ] User has been presented ASCI wireframes for every page and approved them

→ See `references/layout_patterns.md` for wireframe templates and examples
→ See `references/common_mistakes.md` section: Phase 2: Layout Mistakes

---

## Phase 3: Select Visualizations

**Goal**: Choose appropriate chart types and establish visual consistency.

### Chart Type Quick Reference

| Data Question           | Recommended Chart                    |
| ----------------------- | ------------------------------------ |
| Compare categories      | Bar chart (horizontal for 8+ items)  |
| Show trend over time    | Line chart (12+ points)              |
| Part-to-whole (simple)  | Pie/donut (2-5 slices ONLY)          |
| Part-to-whole (complex) | Stacked bar chart                    |
| Distribution            | Histogram or box plot                |
| Correlation             | Scatter plot                         |

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

Use `kpi_card()` for simple metrics, `kpi_card_reference()` for comparisons. Use `reverse_color=True` when lower is better (costs, errors).

### Chart Title Pattern

**IMPORTANT**: Titles go in `vm.Graph(title=...)`, NOT in plotly code.

### REQUIRED OUTPUT: spec/3_visual_design.yaml

Save this file BEFORE proceeding to Phase 4:

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

Before proceeding to Phase 4:

- [ ] Chart types match data types (no pie charts for time series)
- [ ] No anti-patterns used
- [ ] Custom chart needs are identified
- [ ] Color usage is consistent and intentional

→ See `references/chart_selection.md` for detailed decision trees
→ See `references/common_mistakes.md` section: Phase 3: Visualization Mistakes

---

## Phase 4: Implement Dashboard

**Goal**: Build the dashboard **strictly following** Phase 1-3 spec files.

**CRITICAL**: Before writing any code, review the spec files:

- `spec/1_information_architecture.yaml` → Pages, KPIs, data sources
- `spec/2_interaction_ux.yaml` → Layout, grid, filter placement
- `spec/3_visual_design.yaml` → Chart types, colors, custom chart needs

Implementation must match these specs. Any deviation requires documentation with reasoning.

### MCP-First Workflow (Recommended)

**Step 1: Load and Analyze Data**

```
Use: vizro-mcp:load_and_analyze_data(path_or_url="path/to/data.csv")
```

**Step 2: Get Model Schemas**

Schemas define valid properties, required fields, and available options for each component. Fetch schemas for components you plan to use.

```
Use: vizro-mcp:get_model_json_schema(model_name="Dashboard")
Use: vizro-mcp:get_model_json_schema(model_name="Page")
```

**Step 3: Build Dashboard Config**

Create JSON config respecting Phase 1-3 decisions.

**Step 4: Validate and Get Code**

```
Use: vizro-mcp:validate_dashboard_config(dashboard_config={...}, data_infos=[...], custom_charts=[])
```

→ See `references/implementation_guide.md` for complete implementation details
→ See `references/common_mistakes.md` section: Phase 4: Implementation Mistakes

### REQUIRED OUTPUT: spec/4_implementation.yaml

Save this file BEFORE proceeding to Phase 5:

```yaml
# spec/4_implementation.yaml
implementation:
  method: mcp  # or python
  app_file: app.py
  data_files:
    - [list of data files used]

spec_compliance:
  followed_specs: true/false
  deviations:
    - spec_item: [What was specified]
      actual: [What was implemented]
      reason: [Why the deviation was necessary]

custom_charts:
  - name: [Function name]
    purpose: [What it does]
```

### Validation Checklist

Before proceeding to Phase 5, verify against spec files:

- [ ] All pages from `spec/1_information_architecture.yaml` are implemented
- [ ] Layout matches `spec/2_interaction_ux.yaml` (grid, filters, containers)
- [ ] Chart types match `spec/3_visual_design.yaml`
- [ ] Color usage is consistent and intentional
- [ ] Dashboard runs without errors
- [ ] Any deviations are documented in `spec/4_implementation.yaml`

→ See `references/implementation_guide.md` for complete examples → See `references/data_management.md` for dynamic data and caching

---

## Phase 5: Test & Verify

**Goal**: Confirm dashboard works correctly and meets requirements.

### Testing Checklist

```
Functional Testing:
- [ ] Dashboard launches at localhost:8050
- [ ] All pages load without errors
- [ ] Navigation between pages works
- [ ] Filters update visualizations correctly
- [ ] Parameters modify chart behavior
- [ ] No JavaScript errors in browser console
```

### Playwright MCP Testing
Look for `mcp__*playwright__*` tools.

**Basic Testing Flow**:

1. Navigate to dashboard URL
1. Click through all pages
1. Check console for errors
```
Use: playwright:browser_navigate(url="http://localhost:8050")
Use: playwright:browser_click(element="Page Name", ref="...")
Use: playwright:browser_console_messages()
```

### REQUIRED OUTPUT: spec/5_test_report.yaml

Save this file to complete the project:

```yaml
# spec/5_test_report.yaml
testing:
  launch:
    successful: true/false
    url: http://localhost:8050
    errors: []

  navigation:
    all_pages_work: true/false
    issues: []

  console:
    no_errors: true/false
    errors_found: []

user_acceptance:
  requirements_met: true/false
dashboard_ready: true/false
```

### User Acceptance

Return to Phase 1 requirements:

- [ ] Dashboard answers the key questions identified
- [ ] KPIs are visible and accurate
- [ ] User confirms it meets their needs

### Done When

- Dashboard launches without errors, no console errors
- User confirms requirements are met
- All 5 spec files saved in `spec/` directory

---

## Reference Files

| File                                     | When to Read                          |
| ---------------------------------------- | ------------------------------------- |
| `references/information_architecture.md` | Phase 1: Deep dive on requirements    |
| `references/layout_patterns.md`          | Phase 2: Wireframes, component sizing |
| `references/chart_selection.md`          | Phase 3: Chart decision trees         |
| `references/implementation_guide.md`     | Phase 4: Complete Python/MCP examples |
| `references/data_management.md`          | Phase 4: Dynamic data and caching     |
| `references/common_mistakes.md`          | All phases: Anti-patterns to avoid    |

---

## Quick Reference: Vizro Components

**Components**: `Dashboard`, `Page`, `Container`, `Tabs`, `Graph`, `Figure`, `AgGrid`, `Card`, `Filter`, `Parameter`, `Selector`, `Button`

**Key Imports**: `import vizro.models as vm`, `from vizro import Vizro`, `import vizro.plotly.express as px`, `from vizro.tables import dash_ag_grid`, `from vizro.figures import kpi_card, kpi_card_reference`, `from vizro.models.types import capture`
