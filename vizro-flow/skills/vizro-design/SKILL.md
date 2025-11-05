---
name: vizro-design
description: End-to-end guidance for designing effective dashboards from concept through wireframing. This skill provides comprehensive workflows for dashboard design, chart selection, layout planning, and wireframing. Use when creating dashboards, selecting chart types, designing data visualizations, creating wireframes, or planning dashboard implementations. Covers metrics display, KPI visualization, data presentation, analytical interface design, and wireframing patterns. For Vizro implementation, use the vizro-implementation skill.
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
2. Add essential supporting metrics
3. Move detailed metrics to drill-downs
4. Remove "nice to have" metrics

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

**Key pattern**: Three-level architecture: (1) Overview (3-7 KPIs), (2) Detail (tabs/sections), (3) Granular (drill-downs). Global filters at top, tooltips on hover with context.

**Consult** `references/design_principles.md` for progressive disclosure patterns, filter types and placement, tooltip formatting, and drill-down behaviors.

### 7. Validate Design

**Key principle**: Users must identify the most important metric in <3 seconds. Dashboard purpose must be clear without explanation. Test with real users before launch.

**Consult** `references/design_principles.md` for usability, accessibility, and performance checklists. See `references/common_mistakes.md` for testing methods (5-second test, first-click test, think-aloud).

**Quick validation checks**:
- Can users identify the most important metric in <3 seconds?
- Are all chart types appropriate for the data?
- Is text contrast sufficient (4.5:1 minimum)?
- Are all interactions keyboard accessible?

### 8. Create Wireframes

**Key principle**: Create ASCII diagram wireframes first for rapid iteration, then generate simple HTML wireframe after approval. Focus on structure and hierarchy, not colors or fonts.

**Consult** `references/wireframing_guide.md` for ASCII and HTML wireframe templates, grid patterns, and workflow guidance.

**Two-step wireframing**:
1. **ASCII diagram first**: Create text-based box diagram showing layout structure
   - Show inline in conversation for immediate feedback
   - Iterate quickly, create multiple variations
   - Use `+`, `-`, `|` characters for boxes
   - Label all sections: KPI, CHART, TABLE, FILTER, PARAMETER (as defined by Vizro), ACTIONS (as defined by Vizro), CONTAINER, TABS
   - Consider splitting over multiple pages - do each page separately
2. **HTML wireframe second**: Generate after ASCII approval
   - Grayscale only
   - Placeholder boxes for charts
   - Write to file for browser preview
   - Use for stakeholder presentations

**When to use each**:
- ASCII: Quick feedback, layout iteration, multiple variations
- HTML: Browser preview, stakeholder review, final approval

### 9. Build Dashboard

**Key principle**: Decide on implementation approach. For Python dashboards with standard Plotly charts, consider Vizro framework (rapid development, professional styling). For other requirements, implement custom solution.

**For Vizro implementation**: Use the **vizro-implementation skill** which provides comprehensive guidance on:
- When to use Vizro (decision tree)
- MCP installation and setup
- Building with Vizro MCP or live documentation
- Capabilities mapping (automatic vs manual configuration)
- Implementation patterns and troubleshooting

**Vizro** (see vizro-implementation skill for full details):
- **Offers**: Python toolkit with professional themes, colorblind palette, grid/flex layouts, auto-filters (page & container level), all Plotly charts, Cards/KPIs, Containers/Tabs, actions (export, drill-down), multi-page navigation, theme toggle
- **Not for**: CRUD apps, chatbots, very complex UX workflows

**For custom implementation**:
1. Choose appropriate technology stack
2. Implement based on approved wireframe
3. Follow design principles from steps 1-7
4. Test and iterate with users

## Bundled Resources

### References

**`chart_selection_guide.md`** - Chart type selection matrix, decision trees, anti-patterns, data-to-chart mismatches. Read when choosing chart types or fixing inappropriate visualizations.

**`design_principles.md`** - Layout patterns, color strategies, typography, interaction patterns, accessibility requirements, advanced considerations. Read when establishing visual design or making accessible.

**`common_mistakes.md`** - 9 critical errors with solutions, subtle issues, anti-patterns, testing methods. Read when reviewing or fixing existing dashboards.

**`wireframing_guide.md`** - ASCII diagram templates and HTML wireframe templates for rapid dashboard mockups. Read when creating wireframes before implementation.

### Finding Information in References

Use these grep patterns to quickly locate specific guidance:

**Chart selection**:
```bash
grep -i "use for\|avoid when\|best when" references/chart_selection_guide.md
grep -i "anti-pattern\|never use" references/chart_selection_guide.md
grep -i "decision tree" references/chart_selection_guide.md
```

**Design principles**:
```bash
grep -i "contrast\|wcag\|accessibility" references/design_principles.md
grep -i "f-pattern\|hierarchy\|layout" references/design_principles.md
grep -i "color.*scale\|sequential\|diverging" references/design_principles.md
grep -i "tooltip\|filter\|drill-down" references/design_principles.md
```

**Common mistakes**:
```bash
grep -i "problem\|solution" references/common_mistakes.md
grep -i "anti-pattern\|avoid" references/common_mistakes.md
grep -i "test\|checklist" references/common_mistakes.md
```

**Wireframing**:
```bash
grep -i "ascii\|diagram\|template" references/wireframing_guide.md
grep -i "html wireframe\|grid span" references/wireframing_guide.md
grep -i "executive\|operational\|analytical" references/wireframing_guide.md
```

### Scripts and Assets

None. This skill uses only procedural knowledge and references to remain token-efficient.

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

## Best Practices Summary

### Layout
- F-pattern for priority (top-left = critical)
- 5-7 primary metrics maximum
- 24-32px between sections
- 30-40% white space total

### Typography
- Primary metrics: 32-48px bold
- Secondary metrics: 20-28px medium
- Labels: 12-16px regular
- One font family, multiple weights

### Color
- Maximum 3 colors + neutrals
- Consistent color mapping
- 4.5:1 contrast minimum
- Supplement color with patterns

### Charts
- Bar for comparison
- Line for trends
- Avoid 3D always
- Always start bars at zero
- Maximum 5 lines per chart

### Interaction
- Progressive disclosure (3 levels)
- Tooltips on hover
- Global filters at top

### Accessibility
- WCAG AA compliance (4.5:1 text contrast)
- Keyboard navigation for all interactions
- ARIA labels for charts
- Never color alone for meaning

### Performance
- <2 second initial load
- <500ms filter response
- Lazy load below-fold content
- Skeleton screens while loading

## Quick Reference

### Decision Tree for Chart Selection

```
What are you showing?

├─ Comparison of categories
│  └─ Bar chart (horizontal if >7 categories)
│
├─ Change over time
│  ├─ Few points (<12) → Column chart
│  └─ Many points (12+) → Line chart
│
├─ Part-to-whole
│  ├─ Simple (2-5 parts) → Pie/donut
│  └─ Complex or comparative → Stacked bar
│
├─ Distribution
│  ├─ Frequency → Histogram
│  └─ Statistical summary → Box plot
│
└─ Relationship
   └─ Correlation → Scatter plot
```

### Color Usage Checklist

- [ ] Maximum 3 primary colors used
- [ ] Same color for same entity everywhere
- [ ] Sufficient contrast (4.5:1 text, 3:1 elements)
- [ ] Color not sole means of conveying info
- [ ] Tested with color blindness simulator

### Before Shipping Checklist

- [ ] 5-7 metrics maximum on main view
- [ ] Most important metric top-left
- [ ] All chart types appropriate for data
- [ ] Consistent color usage throughout
- [ ] Adequate white space (30-40%)
- [ ] Tooltips provide useful context
- [ ] Keyboard accessible
- [ ] <3 second load time
- [ ] Tested with real users

## Additional Tips

- **Start simple**: Begin with 3 metrics, add only if justified
- **User test early**: Show mockups before building
- **Iterate based on usage**: Track which metrics users actually view
- **Document decisions**: Note why specific charts/layouts were chosen
- **Maintain consistency**: Create and follow a design system
- **Performance matters**: Users abandon slow dashboards
- **Accessibility is essential**: Not optional, plan from start