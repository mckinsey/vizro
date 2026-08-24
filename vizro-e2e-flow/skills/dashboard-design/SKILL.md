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
- [ ] Step 3: Select Visualizations (chart types, KPIs; colors only if user asked)
```

**Interaction style**: When gathering requirements or making design decisions, ask focused questions and present **2–5 numbered options** so the user can choose quickly. Prefer using your client’s built-in multiple-choice or question UI to keep the interaction lightweight and clickable; if that isn’t available, use the same numbered format in plain text

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

- **Limit KPIs**: 5–9 primary metrics per page (7 ± 2 rule)
- **Clear hierarchy**: Overview → Detail → Granular (max 3 levels)
- **Persona-based**: Different users may need different views
- **Decision-focused**: Every metric should inform a decision

### REQUIRED OUTPUT: spec/1_information_architecture.md

Copy the template from [assets/1_information_architecture.md](assets/1_information_architecture.md) to `spec/1_information_architecture.md` at the project root, fill in the placeholders, and save it BEFORE proceeding to Step 2.

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

### Interaction Design

Beyond standard sidebar filters, Vizro supports advanced interactions where clicking a chart or table affects other components. Load the **wiring-vizro-actions** skill for the 6 named interaction patterns (Hierarchical Drill-Down, Single-Page Drill-Down, Comparison Spotlight, Multi-Dimensional Slice, Select & Explore, Data Export) with wireframes, spec entries, and code.

All advanced interactions follow **Source → Control → Target**: a source component (Graph or AgGrid — the components that carry click-data) sets an intermediate control (Filter or Parameter, always with an explicit `id`), which updates data-bearing target components (Graph, AgGrid, Figure, Table).

**Decision flow** — match data shape + user need to a pattern:

```
Hierarchy where detail needs its own page?    → Pattern 1 (Hierarchical Drill-Down)
Hierarchy where detail fits in a container?   → Pattern 2 (Single-Page Drill-Down)
Compare one entity vs many, keep context?     → Pattern 3 (Comparison Spotlight)
2+ categorical dimensions, click one cell?    → Pattern 4 (Multi-Dimensional Slice)
Users need to download data?                  → Pattern 5 (Data Export)
Otherwise → standard filters/parameters are sufficient
```

**When NOT to use advanced interactions**: view-only / executive dashboards, simple filtering needs (sidebar dropdown covers it), fewer than ~5 groups, or when you'd end up with more than 2 interaction patterns on a single page (becomes confusing).

For each interaction, document: source component, source value (column or `"x"`/`"y"`), control id + type (Filter/Parameter), targets, visibility (`visible=False` for highlight patterns), and whether it crosses pages (`show_in_url=True`). See the **wiring-vizro-actions** skill for full templates.

### REQUIRED OUTPUT: spec/2_interaction_ux.md

Copy the template from [assets/2_interaction_ux.md](assets/2_interaction_ux.md) to `spec/2_interaction_ux.md` at the project root, fill in the placeholders (including one ASCII wireframe per page), and save it BEFORE proceeding to Step 3. Delete the entire `## Interactions` section if standard filters/parameters suffice.

### Validation Checklist

Before proceeding to Step 3:

- [ ] Layout follows Vizro constraints
- [ ] Filter placement is intentional and documented
- [ ] User has been presented ASCII wireframes for every page and approved them
- [ ] Each entry in `interactions:` maps to a named pattern from **wiring-vizro-actions** (or the absence of interactions is intentional)
- [ ] User has confirmed the interaction flow

**Anti-patterns**: See [common_mistakes.md](references/common_mistakes.md) section "Step 2: Layout & Interaction Mistakes"

---

## Step 3: Select Visualizations

**Goal**: Choose appropriate chart types and establish visual consistency.

### Chart Types, Colors & KPIs

Load the **selecting-vizro-charts** skill for chart selection, color strategy, anti-patterns, and KPI card rules. Key design decisions:

- Match chart type to data question (bar for comparison, line for trends, pie only for 2–5 slices)
- **Colors**: Do NOT include a `## Colors` section in the spec. Vizro assigns palettes automatically. Only include if the user explicitly requested custom colors in their message.
- Use built-in `kpi_card` / `kpi_card_reference`; never rebuild as custom charts

### REQUIRED OUTPUT: spec/3_visual_design.md

Copy the template from [assets/3_visual_design.md](assets/3_visual_design.md) to `spec/3_visual_design.md` at the project root, fill in the placeholders, and save it BEFORE proceeding to implementation (dashboard-build skill). Do **not** add a `## Colors` section unless the user explicitly asked for custom colors — Vizro assigns palettes automatically.

### Validation Checklist

Before proceeding to implementation (dashboard-build skill):

- [ ] Chart types match data types (no pie charts for time series)
- [ ] No anti-patterns used
- [ ] Custom chart needs are identified
- [ ] A `## Colors` section is **absent** unless the user explicitly requested custom colors

**Anti-patterns**: See [common_mistakes.md](references/common_mistakes.md) section "Step 3: Visualization Mistakes"

## Reference Files

| Reference                                                             | When to Load                                       |
| --------------------------------------------------------------------- | -------------------------------------------------- |
| [information_architecture.md](references/information_architecture.md) | Step 1: Deep dive on requirements                  |
| **designing-vizro-layouts** skill                                     | Step 2: Grid system, component sizing, filters     |
| [wireframe_templates.md](references/wireframe_templates.md)           | Step 2: Wireframe templates and interaction labels |
| **wiring-vizro-actions** skill                                        | Step 2: Cross-filter / cross-highlight / drill-through / export patterns |
| **selecting-vizro-charts** skill                                      | Step 3: Chart types, anti-patterns                 |
| [common_mistakes.md](references/common_mistakes.md)                   | All steps: Anti-patterns to avoid                  |
