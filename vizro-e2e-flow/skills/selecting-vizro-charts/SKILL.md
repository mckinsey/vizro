---
name: selecting-vizro-charts
description: Select chart types, apply Plotly conventions, enforce color strategy, and configure KPI cards when choosing, implementing, or converting Vizro charts.
---

# Vizro Chart Best Practices

## Chart Selection

| Data question            | Chart                          |
|--------------------------|--------------------------------|
| Compare categories       | Bar (horizontal preferred)     |
| Trend over time          | Line (12+ points)              |
| Part-to-whole (simple)   | Pie/donut (2–5 slices only)    |
| Part-to-whole (complex)  | Stacked bar                    |
| Distribution             | Histogram or box               |
| Correlation              | Scatter                        |

**Never use**: 3D charts, pie with 6+ slices, dual Y-axis, bar charts not starting at zero.

## Plotly Conventions

- Plotly Express does **not** aggregate. Pre-aggregate in `app.py` or custom chart functions.
- Bar: sort by value (largest→smallest) unless time-based; always start at zero.
- Line: pre-aggregate and sort by x ascending.
- Remove axis title when ticks are self-explanatory. Remove legend title (keep items only).

## Color Rules

- **Default**: Let Vizro handle colors. No `marker_color`, no hex codes, no `line=dict(color=...)`.
- **When required** (semantic meaning, brand): use `from vizro.themes import palettes, colors`.
- AG Grid and custom figures do **not** auto-pick Vizro palettes — import explicitly.
- Vizro palettes are colorblind-safe. Never use color alone to convey information.

## Custom Charts (`@capture("graph")`)

Use when: aggregation/sorting needed, `update_layout()`/`update_traces()` calls, reference lines, parameter-driven logic, dual-axis, multi-trace `go.Figure()`, shared legend control.

Standard `px` charts expressible via YAML args do **not** need custom functions.

## KPI Cards

- Use built-in `kpi_card` / `kpi_card_reference` from `vizro.figures` in `Figure` model.
- **Never** rebuild KPI cards as custom charts. Exception: strictly impossible with built-in (e.g. dynamic text).
- Titles go in figure args (`_target_: kpi_card` → `title:`), not on the component.

## Deep Dive

Load [chart-best-practices.md](references/chart-best-practices.md) for: full Plotly Express syntax reference, semantic color hex codes, palette details, accessibility rules, and detailed custom chart guidance.
