# Vizro Chart Best Practices

Consolidated reference for chart selection, Plotly implementation, color strategy, and custom charts.

## Chart Type Selection (extended)

- **Comparing values** → Bar (horizontal preferred), grouped bar
- **Change over time** → Line (12+ points), area, or column for discrete periods
- **Parts of a whole** → Pie/donut (2–5 slices only) or stacked bar
- **Distribution** → Histogram, box, violin
- **Relationship** → Scatter, bubble (with caution)
- **Performance vs target** → Bullet, waterfall (custom)

## Plotly Express best practice conventions

- **Bar**: Sort by value (largest to smallest) unless time-based; **always start at zero**.
- **Line**: Pre-aggregate by time/series; sort by x ascending; never pass raw detail-level data and assume correct order.
- **100% stacked bar**: Pre-calculate percentages per category; use `barmode="stack"`; set y-axis range [0, 100] or [0, 1] with `tickformat=".0%"`.
- **Axis/legend**: Remove axis title when ticks make meaning obvious; remove legend title (keep items only). For long or numerous x-axis labels, place legend top-right: `legend=dict(x=1, y=1, xanchor="right", yanchor="top")`.

Plotly Express does **not** aggregate. Pre-aggregate in `app.py` or inside custom chart functions; for YAML-only charts, register pre-aggregated datasets in `data_manager`.

## Color strategy

### Default: let Vizro handle it

Plotly Express charts and KPI cards automatically use Vizro color schemes via the built-in Vizro plotly templates. **Do not** set explicit colors (`color_discrete_sequence`, `color_continuous_scale`, `marker_color`, hex values, etc.) unless the user explicitly requests it. This includes categories with apparent semantic meaning (status flags, source types, plan vs actual) — Vizro's automatic palette handles these well. Qualitative, sequential, diverging, and waterfall colors are all applied automatically.

### AG Grid and manual color assignment

AG Grid does **not** pick up Vizro template colors automatically. When AG Grid cells need coloring (e.g. conditional formatting, heatmaps), always use Vizro palette colors — never invent hex values:

```python
from vizro.themes import palettes, colors
```

Key palettes and colors (see [API reference](https://vizro.readthedocs.io/en/stable/pages/API-reference/themes/) for full list):

| Name                           | Use case                                                      |
| ------------------------------ | ------------------------------------------------------------- |
| `palettes.sequential`          | Continuous data (alias for `sequential_blue`)                 |
| `palettes.sequential_minus`    | Reversed sequential                                           |
| `palettes.diverging`           | Data with a midpoint (use with `color_continuous_midpoint=0`) |
| `palettes.sequential_positive` | Positive-sentiment scale                                      |
| `palettes.sequential_negative` | Negative-sentiment scale                                      |
| `palettes.sequential_warning`  | Warning-sentiment scale                                       |
| `colors.positive`              | Positive status (KPI, waterfall increase)                     |
| `colors.negative`              | Negative status (KPI, waterfall decrease)                     |
| `colors.warning`               | Warning status                                                |
| `colors.info`                  | Informational                                                 |
| `colors.success`               | Success status                                                |
| `colors.error`                 | Error status                                                  |

### Accessibility

- Text on background: min 4.5:1 contrast (WCAG AA); large text 3:1; chart elements 3:1 vs background.
- Never use color alone to convey information; supplement with patterns, icons, or labels.
- Vizro default palettes are colorblind-safe.

## Custom charts

### When to use `@capture("graph")`

- Aggregation or sorting before plotting
- Post-update calls: `update_layout()`, `update_xaxes()`, `update_traces()`
- Reference lines, annotations, thresholds
- Parameter-driven logic (column switching, conditional behavior)
- Dual-axis charts (sync gridlines: `yaxis2=dict(..., overlaying="y", tickmode="sync")`)
- Advanced types: waterfall, bullet, multi-trace `go.Figure()` compositions
- Shared legend control (show once on rightmost chart, hide on others)

Standard `px` charts expressible purely via YAML do **not** need custom functions.

## KPI cards

- Use built-in **`kpi_card`** for simple metrics, **`kpi_card_reference`** for comparisons.
- Use `reverse_color=True` when lower is better (costs, errors).
- **Never** implement KPI cards as custom charts—use `Figure` with `kpi_card` / `kpi_card_reference` from `vizro.figures`. Exception: only when the KPI is strictly not possible with built-in (e.g. dynamically showing text as a KPI).
- Titles go in `vm.Graph(title=...)` or inside the figure args (e.g. `_target_: kpi_card` args), not as a component `title` field for `type: figure`.

## Anti-patterns: use with caution

| Chart type   | Risk                     | Mitigation           |
| ------------ | ------------------------ | -------------------- |
| Bubble       | Size hard to compare     | Add size legend      |
| Stacked Area | Overlapping trends       | Limit to 4 series    |
| Gauge        | Takes space, little info | Use KPI card instead |

## Quick reference: wrong vs right chart

| Data type                 | Wrong         | Right        | Why                       |
| ------------------------- | ------------- | ------------ | ------------------------- |
| Time series (many points) | Bar           | Line         | Lines show continuity     |
| Small differences         | Pie           | Bar          | Bars more precise         |
| Composition over time     | Multiple pies | Stacked area | Shows trend + composition |
| 10+ categories            | Pie           | Bar          | Readable labels           |
| Correlation               | Line          | Scatter      | Line implies sequence     |
