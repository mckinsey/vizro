---
name: dashboard-design
description: Use this skill first when the user wants to design or plan a dashboard, especially Vizro dashboards. Enforces a 3-step workflow (requirements, layout, visualization) before implementation. Activate when the user asks to create, design, or plan a dashboard. For implementation, use the dashboard-build skill after completing Steps 1-3.
---

# Designing Vizro Dashboards

Structured **requirements → layout → visualization** workflow.

## Workflow execution

Run Steps 1–3 in order; each step depends on the prior. Track progress:

```
Dashboard Development Progress:
- [ ] Step 1: Understand Requirements (define end user, dashboard goals, document decisions)
- [ ] Step 2: Design Layout & Interactions (wireframes, filter placement)
- [ ] Step 3: Select Visualizations (chart types, colors, KPIs)
```

**Decision prompts**: For requirements and design choices, ask focused questions and offer **2–5 numbered options** per turn so the user can pick quickly. Use your client’s built-in choice / question UI when it exists; otherwise use the same pattern in plain messages.

**Do not skip steps.** Handle partial context as follows:

- User has data but no requirements → Start at Step 1
- User has requirements but no data → Ask for data or suggest sample data
- User has wireframes → Validate Step 1 decisions, then proceed from Step 2
- User has visual designs/mockups → Validate Steps 1-2 decisions, then proceed from Step 3
- User asks to "just build it" → Explain value of steps, offer to streamline but not skip, ask for data or suggest sample data

**For simple dashboards** (single page, less than 5 charts): Steps 1-3 can be abbreviated but not skipped entirely.

---

## Spec Files: Documenting Decisions

IMPORTANT: Each step produces a spec file in the `spec/` directory to document reasoning, enable collaboration, and allow resumption in future sessions. Create the `spec/` directory at project start.

---

## Step 1: Understand Requirements

**Goal**: Define WHAT information is presented and WHY it matters.

### Key Questions to Discuss

1. **Users**: Who are the end users of this dashboard? Per user type: What decisions do they need to make? What task/job do they need to accomplish?
1. **Goals**: What is the current problem to solve? What is the goal of this dashboard?
1. **Data**: What sources are available? What's the refresh frequency?
1. **Structure**: How many pages or views? What's the logical grouping?

### Design Principles

- **Limit KPIs**: 5 primary metrics per page maximum
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
    kpis: [List of 3-5 key metrics]
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

Load the **designing-vizro-layouts** skill for grid system, component sizing, filter placement, and selector rules. Use the [wireframe templates](references/wireframe_templates.md) when building ASCII wireframes for user approval.

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
  [ASCII wireframe for ALL pages and tab views]
decisions:
  - decision: [What was decided]
    reasoning: [Why this choice was made]
```

### Validation Checklist

Before proceeding to Step 3:

- [ ] Layout follows Vizro constraints
- [ ] Filter placement is intentional and documented
- [ ] User has been presented ASCII wireframes for every page and approved them

**Anti-patterns**: See [common_mistakes.md](references/common_mistakes.md) section "Step 2: Layout Mistakes"

---

## Step 3: Select Visualizations

**Goal**: Choose appropriate chart types and establish visual consistency.

### Chart Types, Colors & KPIs

Load the **selecting-vizro-charts** skill for chart selection, color strategy, anti-patterns, and KPI card rules. Key points for design:

- Match chart type to data question (bar for comparison, line for trends, pie only for 2–5 slices)
- Never use: 3D charts, pie with 6+ slices, dual Y-axis, bar charts not starting at zero
- Let Vizro handle colors by default; specify only for semantic meaning or brand
- Use built-in `kpi_card` / `kpi_card_reference`; never rebuild as custom charts
- Titles go in `vm.Graph(title=...)`, not in Plotly code

### REQUIRED OUTPUT: spec/3_visual_design.yaml

Save this file BEFORE proceeding to implementation (dashboard-build skill):

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

Before proceeding to implementation (dashboard-build skill):

- [ ] Chart types match data types (no pie charts for time series)
- [ ] No anti-patterns used
- [ ] Custom chart needs are identified
- [ ] Color usage is consistent and intentional

**Anti-patterns**: See [common_mistakes.md](references/common_mistakes.md) section "Step 3: Visualization Mistakes"

## Reference Files

| Reference                                                             | When to Load                                       |
| --------------------------------------------------------------------- | -------------------------------------------------- |
| [information_architecture.md](references/information_architecture.md) | Step 1: Deep dive on requirements                  |
| **designing-vizro-layouts** skill                                     | Step 2: Grid system, component sizing, filters     |
| [wireframe_templates.md](references/wireframe_templates.md)           | Step 2: Wireframe templates and interaction labels |
| **selecting-vizro-charts** skill                                      | Step 3: Chart types, colors, anti-patterns         |
| [common_mistakes.md](references/common_mistakes.md)                   | All steps: Anti-patterns to avoid                  |

---

## Quick Reference: Vizro Components

**Available components**: `Dashboard`, `Page`, `Container`, `Tabs`, `Graph`, `Figure`, `AgGrid`, `Card`, `Filter`, `Parameter`, `Selector`, `Button`
