# Cascader Component Design Spec

**Date:** 2026-03-25 **Status:** Draft

## Overview

`Cascader` is a hierarchical dropdown Dash component for `vizro-dash-components`. It lets users navigate and select from a tree-structured option set via cascading side panels. Functionally inspired by feffery-antd-components `AntdCascaderr`; visually identical to `dcc.Dropdown` (trigger, panel chrome, search bar, multi-select bar) with `dbc.Checklist`-style checkboxes in multi mode.

## Props

```typescript
type CascaderOption = {
  label: string;
  value: string | number;
  disabled?: boolean;
  children?: CascaderOption[];  // absence of children = leaf node
};

type CascaderProps = {
  id?: string;
  setProps: (props: Record<string, any>) => void;

  /** Tree-structured options. Nodes with no `children` are leaves. */
  options: CascaderOption[];

  /**
   * Selected value(s). Single value (string|number|null) when multi=false;
   * array of leaf values when multi=true. Only leaf values are ever stored —
   * never intermediate path values.
   */
  value?: string | number | null | (string | number)[];

  /** Enable multi-select. Default false. */
  multi?: boolean;

  /** Show search input. Default true. */
  searchable?: boolean;

  /** Allow clearing the value. Default true. */
  clearable?: boolean;

  /** Placeholder text. Default "Select...". */
  placeholder?: string;

  /** Disable the component. Default false. */
  disabled?: boolean;

  /** Maximum height of the panel in pixels. Default 300. */
  maxHeight?: number;

  className?: string;
  style?: object;
};
```

**Value contract:** `value` always contains only leaf node values. Intermediate (parent) node values are never written to `value`, even when a parent checkbox is clicked (clicking a parent selects/deselects all its descendant leaves). If `value` contains a value not present in `options`, it is silently ignored for display and treated as not selected; it is not written back to `value` automatically. When `multi=false`, empty is represented as `null`; when `multi=true`, empty is represented as `[]`. The `null` form is not valid when `multi=true` and `[]` is not valid when `multi=false`.

## Architecture: Single Flat State Machine

Internal state:

- `activePath: number[]` — indices into the options tree tracking which item is expanded at each column depth. E.g. `[2, 0]` means column 0 item index 2 is expanded, column 1 item index 0 is expanded. Length 0 means only column 0 is visible; length N means N+1 columns are visible. When `options` changes, `activePath` is reset to `[]`.
- `isOpen: boolean` — whether the dropdown panel is visible.
- `searchValue: string` — current search input text (local state, not a Dash prop).

Derived from props + state:

- `columns: CascaderOption[][]` — computed by walking `options` tree following `activePath`. Column 0 is always the root level. Each subsequent column is the `children` array of the active item in the previous column.
- `selectedSet: Set<string|number>` — derived from `value` prop for O(1) membership checks.
- `searchResults: {option: CascaderOption, breadcrumb: string}[]` — when `searchValue` is non-empty, a flat list of matching leaf nodes (label contains search string, case-insensitive) with their ancestor path as a breadcrumb string (e.g. `"Asia › China"`).

## Visual Design

### Trigger (closed)

Identical to `dcc.Dropdown`:

- Border + `var(--Dash-Fill-Inverse-Strong)` background, `border-radius: var(--Dash-Border-Radius)`.
- `CaretDownIcon` on the right, rotates 180° when open.
- **single-select**: displays leaf label as plain text when a value is set; placeholder otherwise. Shows `✕` clear button when `clearable=true` and a value is set.
- **multi-select**: when N = 1 displays the single leaf label as plain text; when N > 1 displays the first label truncated with ellipsis plus a count badge (`"N selected"`). Shows `✕` clear button when `clearable=true` and at least one value is set.
- Focus ring uses `var(--Dash-Fill-Interactive-Strong)`.

### Panel (open)

Floats below trigger via a `position: absolute` div (Radix UI is not available as a source dependency), minimum width = trigger width.

1. **Search bar** (when `searchable=true`): sticky at top, same styling as `dcc.Dropdown` search (magnifying glass icon, inline input, clear button). Matches `dash-dropdown-search-container`.
1. **Select all / Deselect all bar** (when `multi=true`, not shown when `multi=false`): identical to `dcc.Dropdown` `dash-dropdown-actions` bar, always visible when `multi=true`. During search it operates on the search results; without a search it operates on the entire tree.
1. **Column area** (when not searching): side-by-side columns separated by `1px solid var(--Dash-Fill-Disabled)` dividers. The column area as a whole is capped at `maxHeight` px; each column is `max-height: 100%` and scrolls independently.
    - **Parent row**: label + `›` chevron on the right. Active (expanded) row has `var(--Dash-Fill-Interactive-Weak)` background. In multi mode, a checkbox precedes the label; it is checked if all descendant leaves are selected, indeterminate if some are, unchecked otherwise.
    - **Leaf row**: label only (no chevron). In single mode, selected leaf shows `var(--Dash-Fill-Interactive-Weak)` background. In multi mode, a checkbox.
    - Disabled options are dimmed and non-interactive.
1. **Search results** (when searching): renders as a flat `dcc.Dropdown`-style options list. Each row shows the leaf label on the left and a faint breadcrumb path (`"Asia › China"`) right-aligned. In multi mode uses checkboxes.

### CSS

New file `src/ts/css/cascader.css` (imported from the TSX fragment so webpack's `css-loader` bundles it), using only `var(--Dash-)` design tokens — no hardcoded colours. Reuses class names from `dropdown.css` where structure is identical (trigger, search bar, actions bar). Cascader-specific classes prefixed `dash-cascader-`. The panel uses `z-index: 500` (matching `dash-dropdown-content`).

## Interaction Behaviour

### Single-select

- Clicking a leaf: sets `value` to that leaf's value, closes panel.
- Clicking a parent: expands its column to the right (does not set value, does not close).
- Clicking `✕` clear: sets `value` to `null`.
- Panel closes on outside click or Escape.

### Multi-select

- Clicking a leaf checkbox: toggles that leaf in `value`.
- Clicking a parent checkbox: collects all descendant leaf values. Unchecked → add all (→ checked); indeterminate → add all missing descendants (→ checked); checked → remove all (→ unchecked). Panel stays open.
- "Select all": adds all leaf values in the current search results (or entire tree if not searching) to `value`.
- "Deselect all": removes all leaf values in the current search results (or entire tree) from `value`.
- Clicking `✕` clear on trigger: sets `value` to `[]`.

### Search

- Typing filters to leaf nodes whose label contains the search string (case-insensitive).
- Results are shown as a flat list (columns hidden).
- In single-select: selecting a result sets `value`, closes the panel, and clears the search.
- In multi-select: clicking a result checkbox toggles it in `value`; search is not cleared so the user can continue selecting from results. Clearing the search input (via its `✕` or backspace) restores the column view.
- While search is active, clicking a parent row (not its checkbox) in search results is a no-op — the expand action is suppressed. Only leaf selection and parent checkbox clicks are active during search.

### Keyboard (future / stretch)

Not in scope for initial implementation. The component will be mouse/touch only initially.

## File Structure

```
src/ts/
  components/
    Cascader.tsx          # Dash wrapper component (class, exports propTypes + defaultProps)
  fragments/
    Cascader.tsx          # Functional implementation
  css/
    cascader.css          # Component styles (Dash design tokens only)
```

No new npm dependencies. Radix UI is not available as a source import — the panel is implemented as a plain `position: absolute` div. Icons (`CaretDownIcon`, `Cross1Icon`, `MagnifyingGlassIcon`) are inline SVGs copied from `@radix-ui/react-icons` source or implemented as simple Unicode/SVG equivalents.

## Out of Scope

- Keyboard navigation
- Virtual scrolling (options trees are expected to be small-to-medium)
- Lazy-loading of children (all options provided upfront)
- `debounce` prop
- Custom option rendering (labels are strings only)
- `inline` (panel-only) mode
