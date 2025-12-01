---
name: interaction-ux-design
description: Stage 2 of Vizro dashboard development. USE AFTER completing information-architecture. Designs how users navigate and explore data - determines layout logic, flow between overview and detail, placement of filters and controls, and creates wireframes. Must be completed before visual design.
---

# Interaction & UX Design for Vizro Dashboards

**Key Focus**: Decide HOW users navigate and explore data — layout logic, filter placement, and wireframes.

**IMPORTANT: Do not use emojis in dashboard implementations. Emojis in wireframes are for documentation only.**

## OUTPUT PRESERVATION NOTICE

Your outputs from this stage are BINDING CONTRACTS for later stages.

## REQUIRED OUTPUT: spec/2_interaction_ux.yaml

```yaml
# spec/2_interaction_ux.yaml
pages:
  - name: string  # Must match stage 1
    layout_type: "grid" or "flex"
    grid_pattern: list[list[int]] if grid  # e.g., [[0,1], [2,3]]

    containers:
      - name: string
        has_own_filters: boolean

    filter_placement:
      page_level: list[string]  # Left sidebar
      container_level: list[string]  # Inside containers
```

Save this file BEFORE proceeding to visual-data-design.

## Vizro Navigation Architecture

```
Tier 1: Global Navigation
├── Multi-page sidebar (automatic in Vizro)
└── Page selection

Tier 2: Page-level Controls
└── Page filters/parameters (left collapsible sidebar - Vizro requirement)

Tier 3: Component-level Interactions
├── Container-specific filters/parameters
├── Cross-filter, Cross-parameter, Cross-highlight
└── Export data
```

## Vizro Mandatory Layout Structure

```
+--+------------+------------------------------------------------------------------------+
|  |NAV MENU    |                    MAIN CONTENT AREA                                   |
|  |            |                                                                        |
|  |------------|  [KPIs, Charts, Tables arranged here]                                  |
|  |FILTERS/    |                                                                        |
|  |PARAMS      |  CONTAINER: [Name]                                                     |
|  |(Page level)|  [Container Filters/Params] ← These appear IN the main area            |
|  |            |  [Container Components]                                                |
+--+------------+------------------------------------------------------------------------+
```

## Vizro Optimal Layout Strategy

**Standard grid configuration**:
- **8 or 12 columns** for granular control
- **row_min_height="140px"** for consistent sizing

**Component sizing**:
- **KPI cards**: 2-3 columns × 1 row (140px) - optimal size
- **Charts**: minimum 3-4 columns × 3 rows (420px) - ensures proper rendering
- **Tables**: full width, rows based on content
- **Empty cells**: use `-1` for intentional spacing

**Layout principles**:
- ✅ **DO**: Place page-level filters/params in left sidebar
- ✅ **DO**: Add container-level filters ABOVE container in main area
- ✅ **DO**: Give charts at least 3 columns × 3 rows
- ✅ **DO**: Use 2-3 charts per row (side-by-side)
- ✅ **DO**: Assign full width to tables with 6+ columns
- ✅ **DO**: Assign full width ONLY to timeseries line charts
- ✅ **DO**: Use -1 for empty cells when needed
- ❌ **DON'T**: Put filters in main area unless in a container
- ❌ **DON'T**: Make charts smaller than 3×3 (they'll be crowded)
- ❌ **DON'T**: Use full-width for non-timeseries charts

## When to Use Containers

Use `Container` when you need:

- **Logical grouping**: Split page into subsections
- **Scoped controls**: Apply filters/parameters to specific sections only
- **Section titles**: Add clear titles to distinguish content areas

Container controls affect only that container's components (built-in Vizro feature).

## Filter Placement

```
Is this filter needed across multiple visualizations?
├─ YES → Page-level filter (left sidebar)
└─ NO → Container-level filter
```

## Vizro-Specific Constraints

1. **Page Navigation**: Automatic sidebar (left) for multi-page apps
2. **Page Filters**: MUST be in collapsible left sidebar
3. **Layouts**: Use Grid or Flex layout (no absolute positioning)
4. **Components**: Limited to Graph, Table, Card, Figure
5. **Containers**: Can use Tabs for organizing content
6. **Actions**: Export, filter, and parameter actions only

## Deliverables

1. **Layout specification** for each page (grid pattern or flex)
2. **Filter placement** (page-level vs container-level)
3. **ASCII wireframes** for unique pages with interaction annotations

See `references/wireframing_guide.md` for detailed wireframing patterns and examples.

## Validation Checklist

- [ ] Navigation requires max 3 clicks to any information
- [ ] Filter placement follows Vizro constraints
- [ ] Wireframes document all interactions

## Next Step

Proceed to **visual-data-design** skill.
