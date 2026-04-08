---
name: selecting-vizro-charts
description: Use this skill when choosing chart types, applying Plotly Express conventions, configuring colors, or building KPI cards for Vizro dashboards. Activate when the user asks which chart fits their data, needs custom chart functions, wants to set colors or palettes, or is creating KPI metric cards.
---

# Vizro Chart Best Practices

## Chart Selection

| Data question           | Chart                       |
| ----------------------- | --------------------------- |
| Compare categories      | Bar (horizontal preferred)  |
| Trend over time         | Line (12+ points)           |
| Part-to-whole (simple)  | Pie/donut (2–5 slices only) |
| Part-to-whole (complex) | Stacked bar                 |
| Distribution            | Histogram or box            |
| Correlation             | Scatter                     |

**Never use**: 3D charts, pie with 6+ slices, dual Y-axis, bar charts not starting at zero.

## Plotly Conventions

- Plotly Express does **not** aggregate. Pre-aggregate in `app.py` or custom chart functions.
- Bar: sort by value (largest→smallest) unless time-based; always start at zero.
- Line: pre-aggregate and sort by x ascending.
- Remove axis title when ticks are self-explanatory. Remove legend title (keep items only).

## Color Rules

- **Plotly charts & KPI cards**: Do not specify colors — no `marker_color`, hex codes, `color_discrete_map`, or `color_discrete_sequence`. This applies even for categories with apparent semantic meaning. Only override when the user explicitly asks.
- **AG Grid**: Does not pick up Vizro template colors automatically. Use `from vizro.themes import palettes, colors` for cell styling.
- See [chart-best-practices.md](references/chart-best-practices.md) for palette names and import patterns.

## Custom Charts (`@capture("graph")`)

Use when: aggregation/sorting needed, `update_layout()`/`update_traces()` calls, reference lines, parameter-driven logic, dual-axis, multi-trace `go.Figure()`, shared legend control.

**In practice, most bar and line charts need `@capture("graph")` functions** that aggregate data inside. Inline `px.bar(data_frame="raw", x="region", y="revenue")` on detail-level data stacks individual rows as separate rectangles instead of summing — producing visually broken charts. Scatter charts do not need aggregation — each row is one data point.

## KPI Cards

- Use built-in `kpi_card` / `kpi_card_reference` from `vizro.figures` in `Figure` model.
- **Never** rebuild KPI cards as custom charts. Exception: strictly impossible with built-in (e.g. dynamic text).
- Titles go in figure args (`_target_: kpi_card` → `title:`), not on the component.

## Deep Dive

Load [chart-best-practices.md](references/chart-best-practices.md) when you need: extended chart type decision tree, Plotly Express formatting conventions (100% stacked bar, axis/legend cleanup), palette/color names and use cases, accessibility rules, or detailed `@capture("graph")` guidance.
