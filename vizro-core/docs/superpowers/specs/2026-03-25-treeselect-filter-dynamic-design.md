# TreeSelect Filter Dynamic Data Support Design

**Date:** 2026-03-25 **Branch:** feat/cascading-filter **Scope:** Dynamic data support for `column_hierarchy` filters (extends static spec `2026-03-25-treeselect-filter-design.md`)

## Overview

Extend the `column_hierarchy` Filter to support dynamic data sources. When any target figure uses a `_DynamicData` source, the TreeSelect options are recomputed on every page refresh from fresh data, exactly mirroring how standard categorical filters work dynamically. Stale selected leaf values (present in the user's current selection but absent from the refreshed data) are preserved in a `"(Stale selection)"` top-level group — the tree equivalent of how `_get_options` preserves stale flat values by concatenating them into the returned options.

## Dynamic Detection in `pre_build`

The hierarchy `pre_build` branch gains a dynamic detection block inserted **after** building `wide_df` and validating the selector type, but **before** setting `self.selector.options`:

```python
# Dynamic detection — same pattern as the standard path
for target_id in self.targets:
    data_source_name = cast(FigureType, model_manager[target_id])["data_frame"]
    if isinstance(data_manager[data_source_name], _DynamicData):
        self._dynamic = True
        self.selector._dynamic = True
        break

# Only set options for static filters; dynamic filters compute them at runtime in __call__
if not self._dynamic:
    if not self.selector.options:
        built_options = self._get_tree_options(wide_df, self.column_hierarchy)
        _check_no_duplicate_leaves(built_options)
        self.selector.options = built_options
```

Key points:

- `self.selector.options` is only assigned for static filters. For dynamic filters it stays `{}` (the default), which means `not getattr(self.selector, "options", [])` stays `True` — but we do not rely on that condition here; instead we gate options-setting explicitly with `if not self._dynamic`.
- `_check_no_duplicate_leaves` is only called for static filters. For dynamic data, the data shape can change at runtime and duplicates cannot be validated at build time.
- User-supplied `self.selector.options` (non-empty at construction) bypass dynamic detection naturally: if the user explicitly provided options, they are treated as fixed and the filter behaves statically regardless of the data source. This matches the existing pattern where user-supplied `selector.options` prevent `_dynamic = True`.
- `self.selector.value = get_selector_default_value(self.selector)` and the `_filter_isin` action are set unconditionally, unchanged.
- The existing `# TODO: add dynamic support for column_hierarchy` comment is removed.

## `Filter.__call__` Changes

Add an `elif _is_tree_selector(selector):` branch in `__call__` alongside the existing categorical and numerical/temporal branches. The `_validate_targeted_data` and `_validate_column_type` calls at the top of `__call__` remain unchanged — they work on the leaf column (`self.column`) which is set during `pre_build`.

```python
elif _is_tree_selector(selector):
    selector_call_obj = selector(options=self._get_tree_options_dynamic(
        {target: df for target, df in target_to_data_frame.items() if target in self.targets},
        self.column_hierarchy,
        current_value,
    ))
```

`_is_tree_selector` must be added to the `_controls_utils` import in `filter.py` (see Import Changes section below).

## `_get_tree_options_dynamic` Static Method

New static method on `Filter`:

```python
@staticmethod
def _get_tree_options_dynamic(
    target_to_data_frame: dict[ModelID, pd.DataFrame],
    columns: list[str],
    current_value: MultiValueType | SingleValueType | None,
) -> dict[str, Any]:
    """Build tree options from fresh data, preserving stale current_value leaves."""
    # Build wide_df from targets that have all hierarchy columns (silently skip others)
    dfs = [
        df[columns]
        for df in target_to_data_frame.values()
        if all(col in df.columns for col in columns)
    ]
    wide_df = pd.concat(dfs, ignore_index=True).drop_duplicates() if dfs else pd.DataFrame(columns=columns)
    options = Filter._get_tree_options(wide_df, columns)

    # Re-inject stale selected leaves under "(Stale selection)" — parallel to _get_options behaviour
    if current_value:
        current_leaves = current_value if isinstance(current_value, list) else [current_value]
        existing_leaves = _extract_leaf_keys(options)
        stale = sorted(v for v in current_leaves if v not in existing_leaves)
        if stale:
            options["(Stale selection)"] = stale

    return options
```

`_extract_leaf_keys` is imported from `vizro.models._components.form.tree_select` (already imported in the module via `_check_no_duplicate_leaves`; add `_extract_leaf_keys` to the same import line).

The `"(Stale selection)"` group is only added when there are actually stale values. When the user clears their selection or all values are still valid, the group is absent.

## `filter.py` Import Changes

- Add `_extract_leaf_keys` to the import from `vizro.models._components.form.tree_select`
- Add `_is_tree_selector` to the import from `vizro.models._controls._controls_utils`

## Testing

### New tests in `test_filter.py`

**Dynamic detection:**
- `column_hierarchy` targeting a dynamic data source: `filter._dynamic is True` and `filter.selector._dynamic is True` after `pre_build`
- `column_hierarchy` targeting a dynamic data source: `filter.selector.options == {}` after `pre_build` (options not fixed at build time)
- `column_hierarchy` targeting a mix of static and dynamic sources: `_dynamic = True` if any target is dynamic
- `column_hierarchy` with user-supplied `selector=vm.TreeSelect(options=...)`: `_dynamic` stays `False` even when target is dynamic (user-supplied options treated as static)

**`Filter.__call__` (tree path):**
- With no stale values: returned options match freshly built tree, no `"(Stale selection)"` key
- With stale `current_value` entries: stale leaves appear under `"(Stale selection)"` key, sorted
- With `multi=False` and a single stale string value: stale value appears under `"(Stale selection)"`
- Target missing an intermediate hierarchy column is silently excluded in `_get_tree_options_dynamic`
- All targets missing hierarchy columns: returns empty options (no crash)

## Out of Scope

- Duplicate leaf validation at runtime (dynamic data may introduce duplicates; not handled)
- Cascading / dependent filters (one TreeSelect filtering another)
