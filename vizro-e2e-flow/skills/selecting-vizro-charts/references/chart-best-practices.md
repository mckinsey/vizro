# Vizro Chart Best Practices

Consolidated reference for chart selection, Plotly implementation, color strategy, and custom charts.

**When to read:** Choosing chart types, implementing Plotly conventions, applying color strategy, building custom charts or KPI cards.

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

### Default

Let Vizro handle colors for standard charts. Do not set explicit colors (no hex, `marker_color`, `line=dict(color=...)`) unless the user explicitly requests or semantic meaning is required.

### When to specify colors

Use `vizro.themes`:

```python
from vizro.themes import palettes, colors
```

- **Palettes**: `sequential`, `sequential_minus`, `diverging`, `qualitative` (for heatmaps, categorical, etc.)
- **Semantic**: `colors.positive`, `colors.negative`, `colors.warning`, `colors.info` (KPIs, status, conditional formatting)

**Semantic options** (pick one and use consistently):

- **Option A (Teal/Green):** positive `#00B5A9`, negative `#EA5748`, warning `#FFC107`, neutral `#3E495B`
- **Option B (Blue):** positive `#097DFE`, negative `#EA5748`, warning `#FFC107`, neutral `#3E495B`

AG Grid, custom figures, and manual color logic do not pick up Vizro palettes automatically—import and use `palettes`/`colors` explicitly.

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

