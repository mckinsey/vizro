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
- **Flex**: Flexible stacking — `direction="column"` (default) for vertical, `direction="row"` for horizontal. Best used inside a `Container` for simple component groups.

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

- Place KPI cards in the page `Grid`, giving each card **equal columns and equal rows**.
- Divide the 12 columns **evenly** so each card has the same width. All cards must also occupy the **same number of rows** (typically 1 row at 140px).
- Use `-1` for remaining empty cells when the card count doesn't divide evenly into 12.

| KPI count | Columns per card | Grid row pattern                            |
| --------- | ---------------- | ------------------------------------------- |
| 2         | 6                | `[0,0,0,0,0,0, 1,1,1,1,1,1]`               |
| 3         | 4                | `[0,0,0,0, 1,1,1,1, 2,2,2,2]`              |
| 4         | 3                | `[0,0,0, 1,1,1, 2,2,2, 3,3,3]`             |
| 5         | 2                | `[0,0, 1,1, 2,2, 3,3, 4,4, -1,-1]`         |
| 6         | 2                | `[0,0, 1,1, 2,2, 3,3, 4,4, 5,5]`           |

```yaml
# Example: 4 KPI cards in a 12-col grid (3 cols each, 1 row)
layout:
  grid:
    - [0, 0, 0, 1, 1, 1, 2, 2, 2, 3, 3, 3]   # KPI row
    - [4, 4, 4, 4, 4, 4, 5, 5, 5, 5, 5, 5]   # charts below
    - [4, 4, 4, 4, 4, 4, 5, 5, 5, 5, 5, 5]
    - [4, 4, 4, 4, 4, 4, 5, 5, 5, 5, 5, 5]
  row_min_height: "140px"
  type: grid
```

**Exceptions:** Text-heavy Card -> 3+ rows; small table (\<5 cols) -> doesn't need full width; Button -> 1 row. Charts need at least 2-3 rows to avoid looking squeezed.

### Flexible width distributions (new layouts only)

| Layout                 | Column distribution                                |
| ---------------------- | -------------------------------------------------- |
| 3 equal charts         | 4 + 4 + 4                                          |
| Primary + 2 secondary  | 6 + 3 + 3                                          |
| Two-thirds + one-third | 8 + 4                                              |
| Two equal charts       | 6 + 6                                              |
| KPI cards (any count)  | Equal cols each (e.g. 4 cards = 3 cols) + `-1` for remainder |

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

Page-level filters without `targets:` apply to all components whose data includes that filter column. This works when datasets are the same, but can cause "column not found" errors if some components have datasets that lack that column. Use `targets`: only if you want the filter to apply to specific components rather than all components on that page.

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
1. **Actions**: `export_data` and `set_control` actions only

## References

- [Layouts](https://vizro.readthedocs.io/en/latest/pages/user-guides/layouts/)
- [Containers](https://vizro.readthedocs.io/en/stable/pages/user-guides/container/)
