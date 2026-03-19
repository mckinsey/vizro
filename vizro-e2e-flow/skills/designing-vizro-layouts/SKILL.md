---
name: designing-vizro-layouts
description: Use this skill when designing or building Vizro dashboard layouts — grid configuration, component sizing, filter/parameter placement, selector types, or container patterns. Activate when the user is creating wireframes, defining page structure, placing controls, or sizing charts.
---

# Vizro Layout Guidelines

## Core Rules

- Use `type: grid` (not `vm.Layout`). Recommended: **12 columns**, `row_min_height: "140px"`.
- Use `-1` for empty cells. Every component must form a **perfect rectangle** in the grid.
- Place 2–3 charts per row. Full-width only for time-series line charts.

## Component Sizing (12-col grid, 140px rows)

| Component   | Columns | Rows | Height    |
| ----------- | ------- | ---- | --------- |
| KPI Card    | 2–3     | 1    | 140px     |
| Small Chart | 4       | 3    | 420px     |
| Large Chart | 6       | 4–5  | 560–700px |
| Table       | 12      | 4–6  | 560–840px |

**KPI cards**: Wrap in a `Container` with `Flex(direction="row", gap="12px", wrap=True)` layout, then place the container as one full-width row in the page `Grid`. To make cards stretch equally across the available width, add `#container_id .flex-item { flex: 1; }` in `assets/custom.css`. Fallback: place directly in grid at 2–3 cols each with equal width and `-1` for empty cells. Charts need **at least 2–3 rows** to avoid looking squeezed.

## Filter Placement

- **Page-level** (left sidebar): filters shared across multiple components
- **Container-level** (above container): filters scoped to one section
- Prefer Filters over Parameters. Set `targets:` only when components on a page use different datasets.

## Selectors

**Default**: Just provide the column name to `Filter` or `Parameter` — Vizro auto-selects the appropriate selector based on the data type. Only override when the auto-selected selector doesn't fit:

| Data type     | Selector    | Example               |
| ------------- | ----------- | --------------------- |
| 2–4 options   | RadioItems  | Region (N/S/E/W)      |
| 5+ options    | Dropdown    | Category (many)       |
| Numeric range | RangeSlider | Price ($0–$1000)      |
| Single number | Slider      | Year (2020–2025)      |
| Date          | DatePicker  | Order date            |
| Multi-select  | Checklist   | Status (Active, etc.) |

## Deep Dive

Load [layout-guidelines.md](references/layout-guidelines.md) when you need: grid YAML examples (correct vs incorrect), flexible width distributions, container patterns (plain/filled/outlined), visual hierarchy principles, or Vizro platform constraints.
