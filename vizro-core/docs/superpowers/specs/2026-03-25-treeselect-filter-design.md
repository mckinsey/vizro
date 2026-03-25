# TreeSelect Filter Integration Design

**Date:** 2026-03-25
**Branch:** feat/cascading-filter
**Scope:** Static filters only (no dynamic data support in this iteration)

## Overview

Extend `vm.Filter` to support hierarchical column filtering via `TreeSelect`. The user specifies an ordered list of DataFrame columns forming a hierarchy. The filter automatically builds the `TreeSelect` options from the data and filters on the deepest (leaf) column.

## Public API

```python
# Simple string column — existing behaviour unchanged
vm.Filter(column="species")

# Hierarchy — tree mode, defaults to TreeSelect
vm.Filter(column_hierarchy=["continent", "country", "city"])

# With custom TreeSelect config
vm.Filter(
    column_hierarchy=["continent", "country", "city"],
    selector=vm.TreeSelect(multi=False, title="Location"),
)
```

- `column_hierarchy: list[str]` is a new field on `Filter` (default `[]`).
- Exactly one of `column` or `column_hierarchy` must be set; both or neither raises `ValueError`.
- `filter.column` is set automatically to `column_hierarchy[-1]` in `pre_build`, so all existing downstream code (filter action, targeting, title) works unchanged.
- `TreeSelect` is the only allowed selector when `column_hierarchy` is set. Providing any other selector type raises `ValueError`.
- Selector title defaults to `column_hierarchy[-1].title()` (last column name), consistent with existing behaviour.

## Filter.pre_build Changes

### Targeting
When `column_hierarchy` is set, proposed targets are figures whose DataFrames contain **all** columns in `column_hierarchy`. Figures missing any column are excluded (or raise if explicitly targeted).

### Column type
Always treated as `"categorical"` in hierarchy mode. `_validate_column_type` is not called.

### Default selector
Default to `TreeSelect()` if no selector provided. Raise `ValueError` if user provides a non-TreeSelect selector.

### Building options
A new private static method `_get_tree_options(targeted_data, columns)` builds a nested dict from the combined DataFrame:

```python
# columns = ["continent", "country", "city"]
# returns:
{
  "Europe": {
    "France": ["Paris", "Lyon"],
    "Germany": ["Berlin"],
  },
  "Americas": {
    "USA": ["New York"],
  }
}
```

Built by iterating unique values at each level using `groupby`. The method just builds the dict — no validation. Sets `self.selector.options = self.selector.options or self._get_tree_options(...)`.

### Filter action
Uses existing `_filter_isin` with `column = self.column` (the leaf column). No changes to the action layer.

### Dynamic detection
Skipped entirely when `column_hierarchy` is set. Marked with a `# TODO` comment for future dynamic support.

## TreeSelect Model Changes

### New duplicate-leaf validator
A new `@model_validator` checks whether any leaf string value appears more than once across different branches. Raises `ValueError` naming the duplicate values. This catches bad data for both `Filter` and `Parameter` usage.

```python
# Raises ValueError: Duplicate leaf values found in options: {'Bruges'}
vm.TreeSelect(options={"France": ["Bruges"], "Belgium": ["Bruges"]})
```

### `__call__` signature change
Add an optional `options` parameter to accept externally-built options (mirrors `Dropdown.__call__(options)`):

```python
def __call__(self, options=None):
    tree_data = _convert_options(options if options is not None else self.options)
    ...
```

## `_controls_utils.py` Changes

- Import `TreeSelect`
- Add `_is_tree_selector(x) -> TypeIs[TreeSelect]` type-narrowing function
- Update `get_selector_default_value` to handle `TreeSelect`: return `[]` if `multi=True`, else `None`

## `filter.py` Changes

- Add `TreeSelect` to imports from `vizro.models._components.form`
- Add `column_hierarchy: list[str] = Field(default=[], ...)` field
- Make `column: Optional[str] = None` (was required `str`) — validated to be set by model validator
- Add `@model_validator(mode="before")` enforcing exactly one of `column`/`column_hierarchy`
- Add `_get_tree_options` static method
- Update `pre_build` with hierarchy branch

## Testing

### `test_tree_select.py`
- Duplicate leaf values across branches raises `ValueError` naming the duplicates
- `__call__(options=...)` uses passed options instead of `self.options`

### `test_filter.py`
- `column_hierarchy` with no selector defaults to `TreeSelect`, title = last column name
- `column_hierarchy` with `selector=vm.TreeSelect(...)` — custom config respected
- `column_hierarchy` with non-TreeSelect selector raises `ValueError`
- Both `column` and `column_hierarchy` set raises `ValueError`
- Neither set raises `ValueError`
- `_get_tree_options` builds correct nested dict from a simple DataFrame
- `_get_tree_options` with duplicate leaf values in data raises `ValueError` (via TreeSelect validator when options are set)
- `_filter_isin` correctly filters on the leaf column

## Out of Scope

- Dynamic data support (`_dynamic` / `__call__` on Filter for tree selectors)
- Multi-target DataFrames with different schemas (standard existing behaviour applies)
