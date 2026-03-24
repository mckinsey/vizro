# Vizro Layout Guidelines

Single reference for grid layout, component sizing, filter placement, and container patterns. Sections marked "(new layouts only)" apply when designing from scratch; when converting existing dashboards, favor replicating the original layout and apply only the technical constraints.

## Contents

- Grid System (type, columns, row height, rectangularity)
- Component Sizing (KPI cards, flexible widths, layout rules)
- Filter Placement (page vs container, filter targets)
- Container Patterns (when to use, variants)
- Visual Hierarchy (new layouts only)
- Vizro-specific constraints

## Grid System

Vizro provides two layout options:

- **Grid**: Precise control over placement and sizing (recommended for pages)
- **Flex**: Flexible stacking — `direction="column"` (default) for vertical, `direction="row"` for horizontal. Best used inside a `Container` for component groups like KPI card rows.

Use `type: grid` in YAML (not `vm.Layout`, which is deprecated).

### Key principles

- **12 columns recommended** (not enforced) - flexible divisors (1, 2, 3, 4, 6, 12)
- Control height by giving components **more rows**
- Each row height: `row_min_height` (recommended `"140px"`)
- Component height = rows x row_min_height
- Use `-1` for intentional empty cells

```yaml
layout:
  grid: [[0, 1, 2, 3], [4, 4, 5, 5]]
  row_min_height: 140px
  type: grid
```

### Grid rectangularity

Every component must form a **perfect rectangle**. Same component index must span the same column range in every row it appears.

```yaml
# WRONG - component 3 not rectangular
grid:
  - [0, 0, 1, 1, 2, 2, 2, 3, 3, 3, 3, 3]
  - [4, 4, 4, 4, 4, 4, 3, 3, 3, 3, 3, 3]

# CORRECT - component 3 same cols both rows
grid:
  - [0, 0, 1, 1, 2, 2, 2, 3, 3, 3, 3, 3]
  - [4, 4, 4, 4, 4, 4, 4, 3, 3, 3, 3, 3]
```

## Component Sizing

See the quick-reference sizing table in the SKILL.md. Below are expanded patterns:

**KPI card rules:**

- KPI cards should be compact (2-3 columns in a grid, or auto-sized in a flex container).
- **Preferred approach**: Wrap KPI cards in a `Container` with `Flex(direction="row")` layout, then place the container as one full-width component inside the page `Grid`. This avoids awkward empty cells and lets the browser handle equal spacing.
- **Stretching to fill width**: Vizro's `Flex` layout does not expose `flex-grow` on children. To make cards stretch equally, add a CSS rule in `assets/custom.css` targeting the container's `.flex-item` children. Each Vizro flex child is rendered as a `div.flex-item`.
- **Fallback (grid-only)**: When placing KPI cards directly in a grid, keep them at 2-3 columns. All cards must have **equal width**. Use `-1` for remaining empty cells.

```python
# Python: Flex container for KPI cards inside a Grid page
vm.Container(
    id="kpi_banner",
    components=[kpi_1, kpi_2, kpi_3, kpi_4, kpi_5],
    layout=vm.Flex(direction="row", gap="12px", wrap=True),
    variant="plain",
)
# Place as component 0 in page grid: [0,0,0,0,0,0,0,0,0,0,0,0]
```

```css
/* assets/custom.css — make KPI cards stretch to equal width */
#kpi_banner .flex-item {
    flex: 1;
}
```

**Exceptions:** Text-heavy Card -> 3+ rows; small table (\<5 cols) -> doesn't need full width; Button -> 1 row. Charts need at least 2-3 rows to avoid looking squeezed.

### Flexible width distributions (new layouts only)

| Layout                 | Column distribution                                |
| ---------------------- | -------------------------------------------------- |
| 3 equal charts         | 4 + 4 + 4                                          |
| Primary + 2 secondary  | 6 + 3 + 3                                          |
| Two-thirds + one-third | 8 + 4                                              |
| Two equal charts       | 6 + 6                                              |
| KPI cards (any count)  | Flex container (preferred) or 2–3 cols each + `-1` |

### Layout rules (new layouts only)

- Place 2-3 charts per row (side-by-side)
- Full-width only for time-series line charts
- Give charts at least 3 rows (e.g. repeat row pattern with `*[[...]] * 3`)

## Filter Placement

```
Filter needed across multiple visualizations?
+-- YES -> Page-level (left sidebar)
+-- NO  -> Container-level (above container)
```

- **Page-level**: Left collapsible sidebar
- **Container-level**: Above the container they control

### Filter targets

Page-level filters without `targets:` apply to **all** components on the page. This works when every component shares the same dataset. When components use different datasets, omitting `targets:` causes "column not found" for any dataset missing that column. Specify `targets:` only when components use different datasets, listing the ones whose data contains the filter column.

Prefer **Filters over Parameters**. Use Parameters only when Filters can't achieve the goal (e.g. switching which column to plot).

## Container Patterns

| Scenario                  | Use container? |
| ------------------------- | -------------- |
| Group related charts      | Yes            |
| Section needs own filters | Yes            |
| Visual separation needed  | Yes            |
| Simple sequential layout  | No             |

**Variants:** `plain` (default), `filled`, `outlined`.

## Visual Hierarchy (new layouts only)

Users scan in an **F-pattern**: left to right across the top, then down the left side. Place the most important content top-left.

| Position    | Priority       | Grid sizing (12-col)      |
| ----------- | -------------- | ------------------------- |
| Top-left    | Most important | 6 columns (half width)    |
| Top-right   | Second         | 6 columns                 |
| Middle-left | Third          | 4 columns (one-third)     |
| Bottom      | Supporting     | 3 columns (quarter width) |

Use component **size to indicate importance** — larger cells signal higher priority. KPIs at the top, detail tables at the bottom.

## Vizro-specific constraints

1. **Page navigation**: Automatic sidebar (built-in)
1. **Page filters/parameters**: MUST be in collapsible left sidebar
1. **Layouts**: Grid or Flex only (no absolute positioning)
1. **Components**: Graph, AgGrid, Card, Figure
1. **Containers**: Can use Tabs for organizing content
1. **Actions**: Export, filter, and parameter actions only

## References

- [Layouts](https://vizro.readthedocs.io/en/latest/pages/user-guides/layouts/)
- [Containers](https://vizro.readthedocs.io/en/stable/pages/user-guides/container/)
