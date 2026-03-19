# Vizro Layout Guidelines

Single reference for grid layout, component sizing, filter placement, and container patterns.

**When to read:** Design or implementation — grid layout, component sizing, filter placement, selector types. Sections marked "(new layouts only)" apply when designing from scratch; when converting existing dashboards, favor replicating the original layout and apply only the technical constraints.

## Grid System

Vizro provides two layout options:

- **Grid**: Precise control over placement and sizing (recommended)
- **Flex**: Automatic vertical stacking (simple single-column pages only)

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

Based on 12-column grid with `row_min_height="140px"`:

| Component       | Columns   | Rows | Min height |
| --------------- | --------- | ---- | ---------- |
| KPI Card        | 3         | 1    | 140px      |
| Small Chart     | 4         | 3    | 420px      |
| Large Chart     | 6         | 4-5  | 560-700px  |
| Table (AG Grid) | 12 (full) | 4-6  | 560-840px  |

**Exceptions:** Text-heavy Card -> 3+ rows; small table (\<5 cols) -> doesn't need full width; Button -> 1 row. Charts need at least 2-3 rows to avoid looking squeezed.

### Flexible width distributions (new layouts only)

| Layout                 | Column distribution |
| ---------------------- | ------------------- |
| 3 equal charts         | 4 + 4 + 4           |
| Primary + 2 secondary  | 6 + 3 + 3           |
| Two-thirds + one-third | 8 + 4               |
| Two equal charts       | 6 + 6               |
| 4 KPI cards            | 3 + 3 + 3 + 3       |

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

### Filter selector types

**Default**: Just provide the column name to `Filter` or `Parameter` - Vizro auto-selects the selector based on the data type. Only override when the auto-selected selector doesn't fit:

| Data type     | Selector        | Example / when to use    |
| ------------- | --------------- | ------------------------ |
| 2-4 options   | **RadioItems**  | Region (N/S/E/W)         |
| 5+ options    | Dropdown        | Category (many)          |
| Numeric range | **RangeSlider** | Price ($0-$1000)         |
| Single number | **Slider**      | Year (2020-2025)         |
| Date          | **DatePicker**  | Order date               |
| Multi-select  | **Checklist**   | Status (Active, Pending) |

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
