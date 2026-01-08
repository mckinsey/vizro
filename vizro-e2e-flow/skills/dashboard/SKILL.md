---
name: dashboard
description: USE THIS SKILL FIRST when user wants to create, design, or build a dashboard. Do NOT jump to MCP tools directly - this skill enforces a 5-phase workflow (requirements, layout, visualization, implementation, testing) that must be followed. MCP tools like vizro-mcp are only used in Phase 4 after completing Phases 1-3 with the user.
---

# Building Vizro Dashboards

A structured workflow for creating effective data dashboards with Vizro.

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

Each phase produces a spec file in the `spec/` directory. These files:

- **Document reasoning**: Capture why decisions were made
- **Enable collaboration**: Team members can review and provide feedback
- **Support handover**: New team members can understand the design history
- **Allow resumption**: Work can continue from spec files in future sessions

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
- **Role-based**: Different users may need different views
- **Decision-focused**: Every metric should inform a decision

### REQUIRED OUTPUT: spec/1_information_architecture.yaml

Save this file BEFORE proceeding to Phase 2:

```yaml
# spec/1_information_architecture.yaml
dashboard:
  name: [Dashboard Name]
  purpose: [One sentence describing the main goal]

pages:
  - name: [Page Name]
    purpose: [What question does this page answer?]
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
- Use **8 or 12 columns** for width control
- Control height by giving components **more rows**

**Component Sizing** (height = rows × 140px):

| Component | Columns    | Rows | Height |
| --------- | ---------- | ---- | ------ |
| KPI cards | 2-3        | 1    | 140px  |
| Charts    | 3-4        | 3+   | 420px+ |
| Tables    | Full width | 4+   | 560px+ |

**Layout Rules**:

- Place 2-3 charts per row (side-by-side)
- Full-width ONLY for timeseries line charts
- Give charts minimum 3 rows (use `*[[...]] * 3` pattern)
- Use `-1` for intentional empty cells

### Filter Placement

```
Is this filter needed across multiple visualizations?
├─ YES → Page-level filter (left sidebar)
└─ NO → Container-level filter (above container in main area)
```

**Page-level filters**: Always in left collapsible sidebar **Container filters**: Above the container they control

### When to Use Containers

Use `vm.Container` when you need:

- **Logical grouping**: Split page into subsections
- **Scoped controls**: Filters/parameters for specific sections only
- **Section titles**: Clear labels to distinguish content areas

### REQUIRED OUTPUT: spec/2_interaction_ux.yaml

Save this file BEFORE proceeding to Phase 3:

```yaml
# spec/2_interaction_ux.yaml
pages:
  - name: [Must match Phase 1]
    layout_type: grid  # or flex
    grid_columns: 8  # or 12
    grid_pattern: [[0, 1], [2, 3]] # Component placement

    containers:
      - name: [Container Name]
        has_own_filters: true/false

    filter_placement:
      page_level: [column1, column2]
      container_level: [column3]

wireframe: |
  [ASCII wireframe for complex pages - optional]

decisions:
  - decision: [What was decided]
    reasoning: [Why this choice was made]
```

### Validation Checklist

Before proceeding to Phase 3:

- [ ] Layout follows Vizro constraints (filters in sidebar)
- [ ] Navigation requires max 3 clicks to any information
- [ ] Filter placement is intentional and documented
- [ ] User has approved the layout structure

→ See `references/layout_patterns.md` for wireframe templates and examples

---

## Phase 3: Select Visualizations

**Goal**: Choose appropriate chart types and establish visual consistency.

### Chart Type Quick Reference

| Data Question           | Recommended Chart                                     |
| ----------------------- | ----------------------------------------------------- |
| Compare categories      | Bar chart (horizontal for 8+ categories)              |
| Show trend over time    | Line chart (12+ points) or Column chart (\<12 points) |
| Part-to-whole (simple)  | Pie/donut (2-5 slices ONLY)                           |
| Part-to-whole (complex) | Stacked bar chart                                     |
| Distribution            | Histogram or box plot                                 |
| Correlation             | Scatter plot                                          |
| Performance vs target   | Bullet chart                                          |

### Chart Anti-Patterns (Never Use)

- **3D charts**: Distort perception
- **Pie charts with 6+ slices**: Use bar chart instead
- **Dual Y-axis**: Confusing, use separate charts
- **Bar charts not starting at zero**: Misleading

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

Use Vizro built-in `kpi_card` and `kpi_card_reference` from `vizro.figures`:

- `kpi_card()`: Simple metric display with formatting and icons
- `kpi_card_reference()`: Metric with comparison (auto green/red coloring)
- Use `reverse_color=True` when lower is better (costs, errors)

→ See `references/implementation_guide.md` for code examples

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

→ See `references/chart_selection.md` for detailed decision trees → See `references/common_mistakes.md` for anti-patterns to avoid

---

## Phase 4: Implement Dashboard

**Goal**: Build the working dashboard **strictly following** Phase 1-3 spec files.

**CRITICAL**: Before writing any code, review the spec files:

- `spec/1_information_architecture.yaml` → Pages, KPIs, data sources
- `spec/2_interaction_ux.yaml` → Layout, grid, filter placement
- `spec/3_visual_design.yaml` → Chart types, colors, custom chart needs

Implementation must match these specs. Any deviation requires documentation with reasoning.

### MCP-First Workflow (Recommended)

**Step 1: Check MCP Availability**

Look for `vizro-mcp` tools in your available tools.

**Step 2: Load and Analyze Data**

```
Use: load_and_analyze_data(path_or_url="path/to/data.csv")
```

**Step 3: Get Model Schemas**

```
Use: get_model_json_schema(model_name="Dashboard")
Use: get_model_json_schema(model_name="Page")
```

**Step 4: Build Dashboard Config**

Create JSON config respecting Phase 1-3 decisions.

**Step 5: Validate and Get Code**

```
Use: validate_dashboard_config(dashboard_config={...}, data_infos=[...], custom_charts=[])
```

### Key Implementation Patterns

**Dashboard Structure**: `vm.Dashboard` → `vm.Page` → components + controls

**Custom Charts**: Use `@capture("graph")` decorator when you need:

- `update_layout()`, `update_traces()` calls
- Reference lines or annotations
- Data manipulation before visualization

**Tables**: Always use `vm.AgGrid` with `dash_ag_grid()` (never `go.Table`)

**Containers**: Use `vm.Container` for scoped filters that only affect grouped components

**Run**: `uv run python app.py` → Access at http://localhost:8050

→ See `references/implementation_guide.md` for complete code examples

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

### Using Playwright MCP (If Available)

Look for `mcp__*playwright__*` tools.

**Basic Testing Flow**:

1. Navigate to dashboard URL
1. Take snapshot to verify layout
1. Click through all pages
1. Test filter interactions
1. Check console for errors

```
Use: browser_navigate(url="http://localhost:8050")
Use: browser_snapshot()
Use: browser_click(element="Page Name", ref="...")
Use: browser_console_messages()
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

  controls:
    filters_work: true/false
    parameters_work: true/false
    issues: []

  console:
    no_errors: true/false
    errors_found: []

user_acceptance:
  requirements_met: true/false
  feedback: [User feedback if any]

dashboard_ready: true/false
```

### User Acceptance

Return to Phase 1 requirements:

- [ ] Dashboard answers the key questions identified
- [ ] KPIs are visible and accurate
- [ ] User confirms it meets their needs

### Done When

- Dashboard launches without errors, all controls work, no console errors
- User confirms requirements are met
- All 5 spec files saved in `spec/` directory

---

## Reference Files

| File                                     | When to Read                          |
| ---------------------------------------- | ------------------------------------- |
| `references/information_architecture.md` | Phase 1: Deep dive on requirements    |
| `references/layout_patterns.md`          | Phase 2: Wireframes, grid examples    |
| `references/chart_selection.md`          | Phase 3: Chart decision trees         |
| `references/common_mistakes.md`          | Phase 3: Anti-patterns to avoid       |
| `references/implementation_guide.md`     | Phase 4: Complete Python/MCP examples |
| `references/data_management.md`          | Phase 4: Dynamic data and caching     |

---

## Quick Reference: Vizro Components

**Components**: `Dashboard`, `Page`, `Container`, `Tabs`, `Graph`, `Figure`, `AgGrid`, `Card`, `Filter`, `Parameter`, `Button`

**Key Imports**: `import vizro.models as vm`, `from vizro import Vizro`, `import vizro.plotly.express as px`, `from vizro.tables import dash_ag_grid`, `from vizro.figures import kpi_card, kpi_card_reference`, `from vizro.models.types import capture`
