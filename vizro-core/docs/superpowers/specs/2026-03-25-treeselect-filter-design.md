# TreeSelect Filter Integration Design

**Date:** 2026-03-25 **Branch:** feat/cascading-filter **Scope:** Static filters only (no dynamic data support in this iteration)

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
- `filter.column` is set to `column_hierarchy[-1]` **as the first action in `pre_build`**, before any other method is called. `self.column` is `None` between construction and `pre_build`, but `_action_outputs`/`_action_inputs`/`_action_triggers` properties are only ever accessed after `pre_build` runs (this is the existing guarantee in Vizro).
- `TreeSelect` is the only allowed selector when `column_hierarchy` is set. The existing `DISALLOWED_SELECTORS` check is inside an `else` branch (standard path only) and does not apply to the hierarchy path.
- Selector title defaults to `column_hierarchy[-1].title()` (last column name), consistent with existing behaviour.
- `show_in_url` and `visible` work unchanged — `Filter.build()` is not modified. `TreeSelect.value` is `list[str]` (multi=True) or `str | None` (multi=False), both of which are compatible with the existing URL serialisation mechanism used for other selectors.

## `types.py` Changes

`TreeSelect` must be added to `SelectorType` in `types.py`. Currently `TreeSelect` is only listed as usable with `Parameter` (per its docstring). Adding it to `SelectorType` is required so that assigning a `TreeSelect` instance to `Filter.selector: SelectorType | None` passes Pydantic validation. The `TreeSelect` docstring should also be updated to mention `Filter`.

## Filter.pre_build Changes

### Step-by-step ordering for the hierarchy path

The hierarchy path is an `if self.column_hierarchy:` branch at the top of `pre_build`. The existing standard path runs as an `else` branch, completely unchanged.

1. Set `self.column = self.column_hierarchy[-1]`.
1. Load DataFrames for proposed targets using `self.column` (leaf), same as the standard path — `target_to_data_frame` is populated as in the existing code.
1. Call `_validate_targeted_data` on the leaf column as normal to establish the initial target set and valid target list. Then additionally loop over validated targets and exclude any figure whose DataFrame is missing any column in `column_hierarchy` (or raise if that figure was explicitly targeted). This preserves all existing empty-DataFrame error handling.
1. Build `wide_df`: from the already-loaded `target_to_data_frame` (restricted to the validated targets from step 3), select only the `column_hierarchy` columns from each figure's DataFrame, concatenate them, and deduplicate rows. Shape: `len(unique_rows) × len(column_hierarchy)`.
1. Default to `TreeSelect()` if no selector provided. Raise `ValueError` if user provides a non-TreeSelect selector.
1. Set `self._column_type = "categorical"` directly (skip `_validate_column_type`).
1. Set title: `self.selector.title = self.selector.title or self.column.title()`.
1. Set options: `self.selector.options = self.selector.options or self._get_tree_options(wide_df, self.column_hierarchy)`. Then explicitly call `_check_no_duplicate_leaves(self.selector.options)` (imported from `tree_select.py`) — since assigning to a Pydantic field after construction does not re-run model validators, this must be called explicitly for the Filter-built options path. For user-supplied options (non-empty at construction), `_check_no_duplicate_leaves` already ran inside `TreeSelect._validate_options_structure`.
1. Set default value: `self.selector.value = get_selector_default_value(self.selector)`. TreeSelect default value is `[]` (multi=True) or `None` (multi=False) — always no-selection. This is intentional: TreeSelect options are hierarchical and deriving a "sensible first value" would require flattening to leaf values for no clear UX benefit. Assigning `[]` or `None` post-construction does not re-run `_validate_tree_value`, which is safe.
1. Dynamic detection is naturally skipped because `self.selector.options` is already set after step 8, making the condition `not getattr(self.selector, "options", [])` evaluate to `False`. A `# TODO: add dynamic support for column_hierarchy` comment is added in the dynamic block for clarity.
1. Add `_filter_isin` action as normal (on leaf column `self.column`).

### `_get_tree_options(wide_df, columns)` static method

Takes a wide DataFrame (one column per hierarchy level, deduplicated rows) and an ordered list of column names. Returns a nested dict by iterating levels using `groupby`. For a 2-level hierarchy `["continent", "city"]` it returns `{str: list[str]}`; for a 3-level hierarchy `["continent", "country", "city"]` it returns `{str: {str: list[str]}}`. Both are valid `TreeOptionsType`. The method just builds the dict — no validation.

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
    },
}
```

### Filter action

Uses existing `_filter_isin` with `column = self.column` (the leaf column). No changes to the action layer.

### `Filter.__call__` (dynamic path)

Dynamic detection is always naturally skipped for hierarchy filters (step 10 above), so `_dynamic` is never set to `True` and `Filter.__call__` is never invoked for tree selectors. No changes needed to `Filter.__call__`.

## TreeSelect Model Changes

### `options` becomes optional

Change `options: TreeOptionsType` to `options: TreeOptionsType = {}`. This allows `TreeSelect()` to be constructed without arguments for use as a default selector inside `Filter`. The existing `_validate_options_structure` and `_validate_tree_value` validators handle empty dicts gracefully.

### `_check_no_duplicate_leaves` standalone function

Add a standalone function `_check_no_duplicate_leaves(options)` in `tree_select.py`. It raises `ValueError` naming the duplicates if any leaf string appears more than once across different branches. Called from two places:

1. Inside the existing `@model_validator(mode="before") _validate_options_structure` on `TreeSelect`, after structure validation, skipping the check when `options` is empty. This catches duplicates in user-supplied options at construction time.
1. Explicitly by `Filter.pre_build` step 8 (imported from `tree_select.py`) after calling `_get_tree_options`. This catches duplicates in Filter-built options, since model validators do not re-run on post-construction field assignment.

```python
# Raises ValueError: Duplicate leaf values found in options: {'Bruges'}
vm.TreeSelect(options={"France": ["Bruges"], "Belgium": ["Bruges"]})
```

### `__call__` signature change

Add an optional `options` parameter for API symmetry with other categorical selectors, to enable uniform handling in future dynamic support:

```python
def __call__(self, options=None):
    tree_data = _convert_options(options if options is not None else self.options)
    ...
```

`build()` continues to call `self.__call__()` with no arguments; the `options` fallback inside `__call__` uses `self.options`. No change to `build()`.

## `_controls_utils.py` Changes

- Import `TreeSelect` (from `vizro.models._components.form`)
- Add `_is_tree_selector(x) -> TypeIs[TreeSelect]` type-narrowing function
- Update `get_selector_default_value` to handle `TreeSelect`: return `[]` if `multi=True`, else `None` (always no-selection default; rationale in `pre_build` step 9 above)

## `filter.py` Changes

- Add `TreeSelect` to imports from `vizro.models._components.form`
- Import `_check_no_duplicate_leaves` from `vizro.models._components.form.tree_select`
- Add `column_hierarchy: list[str] = Field(default=[], ...)` field
- Update `column` field description to cover the optional/hierarchy case
- Make `column: Optional[str] = None` (was required `str`) — validated to be non-None by `mode="before"` model validator
- Add `@model_validator(mode="before")` enforcing exactly one of `column`/`column_hierarchy`
- Add `_get_tree_options` static method
- Update `pre_build` with hierarchy branch (see step-by-step ordering above), wrapping the entire hierarchy logic in `if self.column_hierarchy:` and the existing logic in `else:`

## Testing

### `test_tree_select.py`

- `TreeSelect()` with no arguments is valid (empty options)
- Duplicate leaf values across branches raises `ValueError` naming the duplicates
- `__call__(options=...)` uses passed options instead of `self.options`

### `test_filter.py`

- `column_hierarchy` with no selector defaults to `TreeSelect`, title = last column name
- `column_hierarchy` with `selector=vm.TreeSelect(...)` — custom config respected (e.g. `multi=False`)
- `column_hierarchy` with non-TreeSelect selector raises `ValueError`
- Both `column` and `column_hierarchy` set raises `ValueError`
- Neither set raises `ValueError`
- `_get_tree_options` builds correct nested dict from a single-figure DataFrame (3-level hierarchy)
- `_get_tree_options` with a 2-level hierarchy returns `{str: list[str]}`
- `_get_tree_options` with two figures with partially overlapping hierarchical data merges correctly
- Data with duplicate leaf values raises `ValueError` (via explicit `_check_no_duplicate_leaves` call in `pre_build`)
- `_filter_isin` correctly filters on the leaf column
- Figure missing an intermediate hierarchy column is excluded from targets (or raises if explicitly targeted)

## Out of Scope

- Dynamic data support (`_dynamic` / `Filter.__call__` for tree selectors)
