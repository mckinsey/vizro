---
name: dashboard-design
description: USE FIRST when asked to design/critique/improve a dashboard. MUST BE USED BEFORE USING THE dashboard-implementation skill and any vizro-mcp tools. End-to-end guidance for designing effective dashboards from concept through wireframing. Provides comprehensive workflows for dashboard design, chart selection, layout planning, color strategy, KPI visualization, data presentation, analytical interface design, and wireframing.
---

# Dashboard Design

## Overview

Effective dashboard design requires balancing information density with clarity, selecting appropriate visualizations, and creating clear visual hierarchy. This guide provides a complete end-to-end process for designing, wireframing, and building user-centered dashboards that enable quick decision-making.

The process spans from initial concept (understanding user needs, selecting metrics) through visual design (layout, colors, interactions), wireframing (low-fidelity mockups), and implementation (with specific Vizro guidance included).

## Design Process

### 1. Define Purpose and Audience

**Key principle**: Every dashboard must serve a specific user role and support clear decisions. Understand who, why, and when before designing anything.

**Essential questions**:

- "Who will use this dashboard and what decisions do they need to make?"
- "What are the 3-5 most important questions this dashboard must answer?"
- "How frequently will users access it?" (daily monitoring, weekly review, executive overview)

### 2. Select and Prioritize Metrics

**Key principle**: Limit primary metrics to 5-7 maximum on main view. Every metric must support a specific decision. Less is more - resist showing everything.

**Consult** `references/common_mistakes.md` for detailed guidance on avoiding information overload and applying the "Does this help make a decision?" test.

**Prioritization method**:

1. Identify critical KPIs (top 3-5)
1. Add essential supporting metrics
1. Move detailed metrics to drill-downs
1. Remove "nice to have" metrics

### 3. Choose Chart Types

**Key principle**: Match chart type to data type and user task. Bar for comparison, line for trends, avoid 3D always. Start bars at zero.

**Consult** `references/chart_selection_guide.md` for comprehensive chart type selection matrix, anti-patterns, and data-to-chart mismatch guidance.

**Quick reference**: See decision tree in Quick Reference section below.

### 4. Design Layout and Hierarchy

**Key principle**: Top-left = most critical KPI. Use size, color, and white space to create 3-4 distinct hierarchy levels. Maintain consistent grid-based spacing (multiples of 8px).

**Consult** `references/design_principles.md` for detailed layout patterns (F-pattern, Z-pattern, grid systems) and visual hierarchy techniques.

### 5. Apply Color Strategy

**Key principles**: Maximum 3 primary colors + neutrals. Use color consistently (same entity = same color everywhere). Text contrast minimum 4.5:1. Never use color alone to convey information.

**Consult** `references/design_principles.md` for color palette structure, sequential/diverging/categorical scales, contrast ratios, and color blindness considerations.

### 6. Design Interactions

**Key pattern**: Three-level architecture: (1) Overview (3-7 KPIs), (2) Detail (tabs/sections), (3) Granular (drill-downs). Global filters in left sidebar (recommended default, unless there's a strong reason otherwise), tooltips on hover with context.

**Consult** `references/design_principles.md` for progressive disclosure patterns, filter types and placement, tooltip formatting, and drill-down behaviors.

### 7. Validate Design

**Key principle**: Users must identify the most important metric in \<3 seconds. Dashboard purpose must be clear without explanation. Test with real users before launch.

**Consult** `references/design_principles.md` for usability, accessibility, and performance checklists. See `references/common_mistakes.md` for testing methods (5-second test, first-click test, think-aloud).

**Quick validation checks**:

- Can users identify the most important metric in \<3 seconds?
- Are all chart types appropriate for the data?
- Is text contrast sufficient (4.5:1 minimum)?
- Are all interactions keyboard accessible?

### 8. Create Wireframes

**Key principle**: Create ASCII diagram wireframes first for rapid iteration, then generate simple HTML wireframe after approval. Focus on structure and hierarchy, not colors or fonts.

**Consult** `references/wireframing_guide.md` for ASCII and HTML wireframe templates, grid patterns, two-step workflow, and detailed guidance on when to use each format.

### 9. Build Dashboard

**Key principle**: Decide on implementation approach based on technology requirements and complexity.

**For Python dashboards with standard components**: Use the **dashboard-implementation skill** which provides decision tree for Vizro suitability, MCP setup, and Python quickstart.

**For custom implementation**: Choose appropriate technology stack, implement based on approved wireframe, and follow design principles from steps 1-7.

## Bundled Resources

### References

**`chart_selection_guide.md`** - Chart type selection matrix, decision trees, anti-patterns, data-to-chart mismatches. Read when choosing chart types or fixing inappropriate visualizations.

**`design_principles.md`** - Layout patterns, color strategies, typography, interaction patterns, accessibility requirements, advanced considerations. Read when establishing visual design or making accessible.

**`common_mistakes.md`** - 9 critical errors with solutions, subtle issues, anti-patterns, testing methods. Read when reviewing or fixing existing dashboards.

**`wireframing_guide.md`** - ASCII diagram templates and HTML wireframe templates for rapid dashboard mockups. Read when creating wireframes before implementation.

## Common Patterns

### Pattern: Executive Dashboard

**Characteristics**:

- 3-5 high-level KPIs only
- Large, prominent numbers
- Clear trend indicators (↑/↓ with %)
- Minimal detail, maximum clarity
- Comparison to targets/benchmarks

**Example structure**:

```
[Primary KPI - Large]     [Secondary KPI]   [Tertiary KPI]
[Trend Chart - Medium]    [Comparison Chart]
[Summary insight text]
```

### Pattern: Operational Dashboard

**Characteristics**:

- 7-12 metrics for monitoring
- Real-time or near-real-time updates
- Alert indicators for exceptions
- Quick actions available
- Drill-downs to detail

**Example structure**:

```
[Alert banner if issues exist]
[Status indicators row]
[Primary metrics grid - 2x3]
[Detailed chart with filters]
```

### Pattern: Analytical Dashboard

**Characteristics**:

- Flexible filtering and segmentation
- Multiple chart types for exploration
- Comparative analysis features
- Export and drill-down capabilities
- Detailed data tables

**Example structure**:

```
[Filter panel - top]
[Primary insight - large]
[Comparison charts - 2 columns]
[Detailed table - bottom]
```
