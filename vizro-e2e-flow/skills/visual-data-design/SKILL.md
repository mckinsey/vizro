---
name: visual-data-design
description: Stage 3 of Vizro dashboard development. USE AFTER completing interaction-ux-design. Translates wireframes into visually compelling and clear designs - selects appropriate chart types, establishes visual hierarchy, defines color strategy, and ensures data storytelling. Must be completed before development.
---

# Visual & Data Design for Vizro Dashboards

**Key Focus**: Choose chart types, establish visual hierarchy, and define color strategy.

## OUTPUT PRESERVATION NOTICE

Your outputs from this stage are BINDING CONTRACTS for implementation.

## REQUIRED OUTPUT: spec/3_visual_design.yaml

```yaml
# spec/3_visual_design.yaml
charts_needing_custom_implementation:
  - name: string
    reason: "has_reference_line" or "has_annotations" or "needs_data_processing"

components_needing_colors:
  - name: string
    reason: string
    color_choice: list[string]
```

Save this file BEFORE proceeding to development-implementation.

## Chart Selection

For detailed guidance, see:

- `references/chart_selection_guide.md` - Chart type decision trees
- `references/common_mistakes.md` - Anti-patterns to avoid

## When to Use Custom Charts

Use custom charts with `@capture("graph")` decorator when:

- You need `update_layout`, `update_xaxes`, `update_traces` calls
- You need data manipulation before visualization
- You want reference lines, annotations, or custom interactions
- Standard `plotly.express` doesn't provide required customization

Implementation details are in **development-implementation** skill.

## Vizro Color Strategy

**IMPORTANT: Use Vizro defaults for standard charts** - do NOT specify colors in scatter, line, bar, etc.

**Vizro core palette** (use only when colors must be specified):

```python
vizro_colors = [
    "#00b4ff",  # Bright blue
    "#ff9222",  # Orange
    "#3949ab",  # Deep blue
    "#ff5267",  # Pink/red
    "#08bdba",  # Teal
    "#fdc935",  # Yellow
    "#689f38",  # Green
    "#976fd1",  # Purple
    "#f781bf",  # Light pink
    "#52733e",  # Olive
]

# Semantic colors
success_color = "#689f38"  # Green - positive
warning_color = "#ff9222"  # Orange - caution
error_color = "#ff5267"  # Pink/red - negative
neutral_color = "gray"  # Neutral/inactive
```

## Vizro Components

**Available**: `Dashboard`, `Page`, `Container`, `Tabs`, `Graph`, `Figure`, `AgGrid`, `Card`, `Filter`, `Parameter`, `Button`

**Important**: Always use `vm.AgGrid` for tables (not `vm.Table` or `go.Table`).

## Layout Strategies

**Optimal Grid Strategy**:

- **8 or 12 columns** with `row_min_height="140px"`
- 8 columns for standard layouts, 12 columns for finer control
- **KPI cards**: 2-3 columns × 1 row (140px height)
- **Charts**: minimum 3-4 columns × 3 rows (420px height)

**When to use Flex**: Only for very simple pages where automatic spacing is acceptable.

See `references/design_principles.md` for detailed layout patterns and visual hierarchy guidance.

## KPI Card Pattern

Use Vizro built-in KPI cards (`kpi_card`, `kpi_card_reference` from `vizro.figures`):

- `value_format` for formatting (e.g., `"${value:,.0f}"`)
- `kpi_card_reference()` for comparison with automatic green/red coloring
- `reverse_color=True` when lower is better (costs, errors)

## Chart Title Pattern

**Important**: Titles go in `vm.Graph`, NOT in plotly code:

```python
# ✅ CORRECT
vm.Graph(
    figure=px.scatter(df, x="width", y="length", color="species"),
    title="Chart Title Here",
    header="Additional context",
    footer="SOURCE: **Data source**",
)

# ❌ WRONG - Don't put title in plotly
vm.Graph(figure=px.scatter(df, x="width", y="length", title="Title"))
```

## Validation Checklist

- [ ] All charts appropriate for their data types
- [ ] Color usage is consistent
- [ ] Custom chart needs are documented in spec

## Next Step

Proceed to **development-implementation** skill.
