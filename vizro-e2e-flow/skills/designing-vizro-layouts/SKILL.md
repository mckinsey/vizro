---
name: designing-vizro-layouts
description: Apply Vizro grid layout rules, component sizing, filter placement, and container patterns when designing or implementing dashboard layouts.
---

# Vizro Layout Guidelines

## Core Rules

- Use `type: grid` (not `vm.Layout`). Recommended: **12 columns**, `row_min_height: "140px"`.
- Use `-1` for empty cells. Every component must form a **perfect rectangle** in the grid.
- Place 2–3 charts per row. Full-width only for time-series line charts.

## Component Sizing (12-col grid, 140px rows)

| Component   | Columns | Rows | Height    |
|-------------|---------|------|-----------|
| KPI Card    | 3       | 1    | 140px     |
| Small Chart | 4       | 3    | 420px     |
| Large Chart | 6       | 4–5  | 560–700px |
| Table       | 12      | 4–6  | 560–840px |

Charts need **at least 2–3 rows** to avoid looking squeezed.

## Filter Placement

- **Page-level** (left sidebar): filters shared across multiple components
- **Container-level** (above container): filters scoped to one section
- Prefer Filters over Parameters. Always set `targets:` when using pre-aggregated data.

## Selector by Data Type

| Data type     | Selector       | Example              |
|---------------|----------------|----------------------|
| 2–4 options   | RadioItems     | Region (N/S/E/W)     |
| 5+ options    | Dropdown       | Category (many)      |
| Numeric range | RangeSlider    | Price ($0–$1000)     |
| Single number | Slider         | Year (2020–2025)     |
| Date          | DatePicker     | Order date           |
| Multi-select  | Checklist      | Status (Active, etc.)|

## Deep Dive

Load [layout-guidelines.md](references/layout-guidelines.md) for: flexible width distributions, container patterns and styling, wireframe labels, Vizro-specific constraints, and full reference links.
