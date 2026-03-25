# Cascade Component Design Spec

**Date:** 2026-03-25
**Status:** Approved

## Overview

`Cascade` is a hierarchical dropdown Dash component for `vizro-dash-components`. It lets users navigate and select from a tree-structured option set via cascading side panels. Functionally inspired by feffery-antd-components `AntdCascader`; visually identical to `dcc.Dropdown` (trigger, panel chrome, search bar, multi-select bar) with `dbc.Checklist`-style checkboxes in multi mode.

## Props

```typescript
type CascadeOption = {
  label: string;
  value: string | number;
  disabled?: boolean;
  children?: CascadeOption[];  // absence of children = leaf node
};

type CascadeProps = {
  id?: string;
  setProps: (props: Record<string, any>) => void;

  /** Tree-structured options. Nodes with no `children` are leaves. */
  options: CascadeOption[];

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

  className?: string;
  style?: object;
};
```

**Value contract:** `value` always contains only leaf node values. Intermediate (parent) node values are never written to `value`, even when a parent checkbox is clicked (clicking a parent selects/deselects all its descendant leaves).

## Architecture: Single Flat State Machine

Internal state:

- `activePath: number[]` — indices into the options tree tracking which item is expanded at each column depth. E.g. `[2, 0]` means column 0 item index 2 is expanded, column 1 item index 0 is expanded. Length = number of open columns − 1.
- `isOpen: boolean` — whether the dropdown panel is visible.
- `searchValue: string` — current search input text (local state, not a Dash prop).

Derived from props + state:

- `columns: CascadeOption[][]` — computed by walking `options` tree following `activePath`. Column 0 is always the root level. Each subsequent column is the `children` array of the active item in the previous column.
- `selectedSet: Set<string|number>` — derived from `value` prop for O(1) membership checks.
- `searchResults: {option: CascadeOption, breadcrumb: string}[]` — when `searchValue` is non-empty, a flat list of matching leaf nodes (label contains search string, case-insensitive) with their ancestor path as a breadcrumb string (e.g. `"Asia › China"`).

## Visual Design

### Trigger (closed)

Identical to `dcc.Dropdown`:

- Border + `var(--Dash-Fill-Inverse-Strong)` background, `border-radius: var(--Dash-Spacing)`.
- `CaretDownIcon` (Radix UI) on the right, rotates 180° when open.
- **single-select**: displays leaf label as plain text; or placeholder if no value.
- **multi-select**: displays leaf labels comma-separated; count badge (`"N selected"`) when N > 1; clear `✕` button when `clearable=true` and a value is set.
- Focus ring uses `var(--Dash-Fill-Interactive-Strong)`.

### Panel (open)

Floats below trigger via Radix UI `Popover`, minimum width = trigger width.

1. **Search bar** (when `searchable=true`): sticky at top, same styling as `dcc.Dropdown` search (magnifying glass icon, inline input, clear button). Matches `dash-dropdown-search-container`.
2. **Select all / Deselect all bar** (when `multi=true`): identical to `dcc.Dropdown` `dash-dropdown-actions` bar, only shown when not searching.
3. **Column area** (when not searching): side-by-side columns separated by `1px solid var(--Dash-Fill-Disabled)` dividers. Each column scrolls independently if taller than `maxHeight / numColumns`.
   - **Parent row**: label + `›` chevron on the right. Active (expanded) row has `var(--Dash-Fill-Interactive-Weak)` background. In multi mode, a checkbox precedes the label; it is checked if all descendant leaves are selected, indeterminate if some are, unchecked otherwise.
   - **Leaf row**: label only (no chevron). In single mode, selected leaf shows `var(--Dash-Fill-Interactive-Weak)` background. In multi mode, a checkbox.
   - Disabled options are dimmed and non-interactive.
4. **Search results** (when searching): renders as a flat `dcc.Dropdown`-style options list. Each row shows the leaf label on the left and a faint breadcrumb path (`"Asia › China"`) right-aligned. In multi mode uses checkboxes.

### CSS

New file `src/css/cascade.css` using only `var(--Dash-)` design tokens — no hardcoded colours. Reuses class names from `dropdown.css` where structure is identical (trigger, search bar, actions bar). Cascade-specific classes prefixed `dash-cascade-`.

## Interaction Behaviour

### Single-select

- Clicking a leaf: sets `value` to that leaf's value, closes panel.
- Clicking a parent: expands its column to the right (does not set value, does not close).
- Clicking `✕` clear: sets `value` to `null`.
- Panel closes on outside click or Escape.

### Multi-select

- Clicking a leaf checkbox: toggles that leaf in `value`.
- Clicking a parent checkbox: collects all descendant leaf values and adds/removes them all from `value` (checked → add all; indeterminate/unchecked → remove all). Panel stays open.
- "Select all": adds all leaf values in the current search results (or entire tree if not searching) to `value`.
- "Deselect all": removes all leaf values in the current search results (or entire tree) from `value`.
- Clicking `✕` clear on trigger: sets `value` to `[]`.

### Search

- Typing filters to leaf nodes whose label contains the search string (case-insensitive).
- Results are shown as a flat list (columns hidden).
- Selecting from search results behaves the same as selecting from columns, then clears the search.
- Clearing search restores the column view.

### Keyboard (future / stretch)

Not in scope for initial implementation. The component will be mouse/touch only initially.

## File Structure

```
src/ts/
  components/
    Cascade.tsx          # Dash wrapper component (class, exports propTypes + defaultProps)
  fragments/
    Cascade.tsx          # Functional implementation
  css/
    cascade.css          # Component styles (Dash design tokens only)
```

No new npm dependencies required. Uses Radix UI `Popover` (already available via dcc), `@radix-ui/react-icons` `CaretDownIcon`, `Cross1Icon`, `MagnifyingGlassIcon` (same as dcc.Dropdown).

## Out of Scope

- Keyboard navigation
- Virtual scrolling (options trees are expected to be small-to-medium)
- Lazy-loading of children (all options provided upfront)
- `debounce` prop
- Custom option rendering (labels are strings only)
- `inline` (panel-only) mode
