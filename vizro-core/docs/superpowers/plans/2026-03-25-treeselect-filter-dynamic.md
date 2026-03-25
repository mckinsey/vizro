# TreeSelect Filter Dynamic Data Support Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `column_hierarchy` filters dynamic — when any target uses a `_DynamicData` source, TreeSelect options are recomputed on each page refresh from fresh data, with stale selected values preserved under a `"(Stale selection)"` group.

**Architecture:** Three changes to `filter.py`: (1) dynamic detection in `pre_build`'s hierarchy branch that skips fixing options at build time, (2) a new `_get_tree_options_dynamic` static method that rebuilds options from fresh DataFrames and injects stale values, (3) a `_is_tree_selector` branch in `Filter.__call__` that invokes the new method at runtime.

**Tech Stack:** Python, Pydantic v2, pandas, Vizro (VizroBaseModel, data_manager, model_manager)

---

## Codebase context

### How dynamic filters work (existing pattern)

In `Filter.pre_build` (standard/else path, `src/vizro/models/_controls/filter.py:356-367`), after setting options/min/max, if any target's data source is `_DynamicData` and the selector doesn't have manually-set options/min/max, `self._dynamic = True` and `self.selector._dynamic = True` are set.

At runtime, `Filter.__call__` (`filter.py:186-219`) is invoked with fresh `target_to_data_frame` and `current_value`. For categorical selectors it calls `selector(options=self._get_options(targeted_data, current_value))`. The `_get_options` method concatenates `current_value` into the options so stale selections remain visible.

### Hierarchy branch in `pre_build`

The `if self.column_hierarchy:` branch is at `filter.py:228-305`. It currently:
1. Sets `self.column = self.column_hierarchy[-1]` (line 230)
2. Loads data, validates targets (lines 232-264)
3. Builds `wide_df` (lines 267-268)
4. Validates selector is TreeSelect (lines 271-275)
5. Sets `self._column_type = "categorical"` (line 277)
6. Sets title (line 278)
7. Sets options if not user-supplied (lines 281-284) — **this is where dynamic detection goes**
8. Sets value (line 286)
9. Has a `# TODO: add dynamic support for column_hierarchy` comment (line 290)
10. Adds `_filter_isin` action (lines 292-300)

### `Filter.__call__`

`filter.py:186-219`. The selector-type dispatch is at lines 205-209. The tree selector branch needs to be added here. `_is_tree_selector` is in `_controls_utils.py` but not yet imported in `filter.py`.

### Imports needed in `filter.py`

Current import from `_controls_utils` (line 20-29): does not include `_is_tree_selector`.
Current import from `tree_select` (line 19): `from vizro.models._components.form.tree_select import _check_no_duplicate_leaves` — needs `_extract_leaf_keys` added.

### Key test fixtures

- `managers_column_hierarchy` (defined at `test_filter.py:1242`): creates a page with two static graphs sharing `continent/country/city` columns. Use this as the basis for a dynamic version.
- `managers_one_page_two_graphs_with_dynamic_data` (conftest.py:134): page with two graphs using `"gapminder_dynamic_first_n_last_n"` as data source.
- `gapminder_dynamic_first_n_last_n_function` (conftest.py:29): returns a lambda; assign to `data_manager["gapminder_dynamic_first_n_last_n"]` inside the test.
- `TestFilterHierarchyPreBuild` class (test_filter.py:1269): existing static hierarchy tests. New dynamic pre_build tests go in a new class `TestFilterHierarchyPreBuildDynamic`.
- `TestFilterCall` class (test_filter.py — search for `class TestFilterCall`): existing dynamic `__call__` tests. New tree call tests go in a new class `TestFilterCallTree`.

### Running tests

From `vizro-core/` directory: `hatch run test-unit tests/unit/vizro/models/_controls/test_filter.py -x -q`

---

## File Structure

| File | Change |
|------|--------|
| `src/vizro/models/_controls/filter.py` | Add `_is_tree_selector` import, add `_extract_leaf_keys` import, add dynamic detection block in hierarchy `pre_build`, add `_get_tree_options_dynamic` static method, add tree branch in `__call__` |
| `tests/unit/vizro/models/_controls/test_filter.py` | Add `TestFilterHierarchyPreBuildDynamic` class and `TestFilterCallTree` class |

---

## Task 1: Dynamic detection in `pre_build` and imports

**Files:**
- Modify: `src/vizro/models/_controls/filter.py:19-29, 277-290`
- Test: `tests/unit/vizro/models/_controls/test_filter.py` (new class `TestFilterHierarchyPreBuildDynamic`)

### Background

The hierarchy path currently always sets `self.selector.options` at build time (lines 281-284). For dynamic filters this must be skipped so options can be recomputed at runtime. Dynamic detection is identical to the standard path (`filter.py:356-367`).

The existing `# TODO: add dynamic support for column_hierarchy` comment at line 290 is removed.

A fixture for a page with a column_hierarchy dynamic data source is needed. The existing `managers_one_page_two_graphs_with_dynamic_data` fixture uses `"gapminder_dynamic_first_n_last_n"` data but that fixture's graphs only have gapminder columns (`continent`, `country`, etc.) — which works for 2-level hierarchy tests. However, `gapminder` has `continent` and `country` columns but NOT `city`. So use `["continent", "country"]` as the hierarchy in dynamic tests.

- [ ] **Step 1: Write the failing tests**

Add a new fixture and test class in `test_filter.py`. Append after the existing `TestFilterHierarchyPreBuild` class (after line ~1358):

```python
@pytest.fixture
def managers_column_hierarchy_dynamic(gapminder_dynamic_first_n_last_n_function):
    """Page with one graph using dynamic gapminder data (has continent and country columns)."""
    data_manager["gapminder_dynamic_first_n_last_n"] = gapminder_dynamic_first_n_last_n_function
    vm.Page(
        id="test_page",
        title="Page Title",
        components=[vm.Graph(id="fig_dynamic", figure=px.scatter("gapminder_dynamic_first_n_last_n", x="continent", y="country"))],
    )
    Vizro._pre_build()


class TestFilterHierarchyPreBuildDynamic:
    def test_dynamic_flag_set(self, managers_column_hierarchy_dynamic):
        f = vm.Filter(column_hierarchy=["continent", "country"])
        model_manager["test_page"].controls = [f]
        f.pre_build()
        assert f._dynamic is True
        assert f.selector._dynamic is True

    def test_options_not_set_for_dynamic_filter(self, managers_column_hierarchy_dynamic):
        f = vm.Filter(column_hierarchy=["continent", "country"])
        model_manager["test_page"].controls = [f]
        f.pre_build()
        assert f.selector.options == {}

    def test_dynamic_flag_not_set_for_static_data(self, managers_column_hierarchy):
        # managers_column_hierarchy uses static data frames
        f = vm.Filter(column_hierarchy=["continent", "country", "city"])
        model_manager["test_page"].controls = [f]
        f.pre_build()
        assert f._dynamic is False
        assert f.selector._dynamic is False

    def test_user_supplied_options_prevent_dynamic(self, managers_column_hierarchy_dynamic):
        # User-supplied options → treated as static regardless of data source
        f = vm.Filter(
            column_hierarchy=["continent", "country"],
            selector=vm.TreeSelect(options={"Europe": ["France", "Germany"]}),
        )
        model_manager["test_page"].controls = [f]
        f.pre_build()
        assert f._dynamic is False
        assert f.selector._dynamic is False
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
hatch run test-unit tests/unit/vizro/models/_controls/test_filter.py::TestFilterHierarchyPreBuildDynamic -x -q
```

Expected: FAIL (dynamic detection not yet implemented)

- [ ] **Step 3: Add imports to `filter.py`**

In `filter.py` line 19, change:
```python
from vizro.models._components.form.tree_select import _check_no_duplicate_leaves
```
to:
```python
from vizro.models._components.form.tree_select import _check_no_duplicate_leaves, _extract_leaf_keys
```

In `filter.py` lines 20-29, add `_is_tree_selector` to the `_controls_utils` import:
```python
from vizro.models._controls._controls_utils import (
    SELECTORS,
    _is_boolean_selector,
    _is_categorical_selector,
    _is_numerical_temporal_selector,
    _is_tree_selector,
    check_control_targets,
    get_control_parent,
    get_selector_default_value,
    warn_missing_id_for_url_control,
)
```

- [ ] **Step 4: Add dynamic detection block in hierarchy `pre_build`**

In `filter.py`, replace the options-setting block and the TODO comment (lines 281-290):

```python
# Before (lines 281-290):
            # Build options if not user-supplied; validate for duplicate leaves
            if not self.selector.options:
                built_options = self._get_tree_options(wide_df, self.column_hierarchy)
                _check_no_duplicate_leaves(built_options)
                self.selector.options = built_options

            self.selector.value = get_selector_default_value(self.selector)

            # Dynamic detection is naturally skipped: options is now non-empty so the condition
            # `not getattr(self.selector, "options", [])` is False.
            # TODO: add dynamic support for column_hierarchy
```

```python
# After:
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

            self.selector.value = get_selector_default_value(self.selector)
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
hatch run test-unit tests/unit/vizro/models/_controls/test_filter.py::TestFilterHierarchyPreBuildDynamic -x -q
```

Expected: 4 tests PASS

- [ ] **Step 6: Run the full filter test suite to check nothing broke**

```bash
hatch run test-unit tests/unit/vizro/models/_controls/test_filter.py -x -q
```

Expected: all tests PASS

- [ ] **Step 7: Commit**

```bash
git add src/vizro/models/_controls/filter.py tests/unit/vizro/models/_controls/test_filter.py
git commit -m "feat: add dynamic detection for column_hierarchy filters in pre_build"
```

---

## Task 2: `_get_tree_options_dynamic` static method and `Filter.__call__` tree branch

**Files:**
- Modify: `src/vizro/models/_controls/filter.py` (add static method after `_get_tree_options`, add branch in `__call__`)
- Test: `tests/unit/vizro/models/_controls/test_filter.py` (new class `TestFilterCallTree`)

### Background

`Filter.__call__` is only invoked at runtime for dynamic filters (when `self._dynamic is True`). It receives `target_to_data_frame` (freshly loaded) and `current_value` (the selector's current value from the browser). The new tree branch calls `_get_tree_options_dynamic` which rebuilds the nested dict from fresh data, then injects any stale `current_value` leaves under `"(Stale selection)"`.

The `__call__` dispatch at `filter.py:205-209`:
```python
        if _is_categorical_selector(selector):
            selector_call_obj = selector(options=self._get_options(targeted_data, current_value))
        elif _is_numerical_temporal_selector(selector):
            _min, _max = self._get_min_max(targeted_data, current_value)
            selector_call_obj = selector(min=_min, max=_max)
```

The guard component wrapping at lines 212-217 applies to ALL branches and stays unchanged.

For the tests, `Filter.__call__` requires the filter to have been through `pre_build`. Use the `managers_column_hierarchy_dynamic` fixture to set up a dynamic filter, then call it directly with crafted `target_to_data_frame`.

Look at existing `TestFilterCall` for the pattern (search for `target_to_data_frame` fixture in that file).

- [ ] **Step 1: Write the failing tests**

Append a new `TestFilterCallTree` class after `TestFilterHierarchyPreBuildDynamic`:

```python
@pytest.fixture
def tree_filter_pre_built(managers_column_hierarchy_dynamic):
    """Pre-built dynamic tree filter targeting fig_dynamic."""
    f = vm.Filter(
        column_hierarchy=["continent", "country"],
        targets=["fig_dynamic"],
        selector=vm.TreeSelect(id="tree_selector_id"),
    )
    model_manager["test_page"].controls = [f]
    f.pre_build()
    return f


class TestFilterCallTree:
    def test_call_returns_fresh_options(self, tree_filter_pre_built):
        fresh_df = pd.DataFrame({"continent": ["Europe", "Asia"], "country": ["France", "Japan"]})
        result = tree_filter_pre_built(
            target_to_data_frame={"fig_dynamic": fresh_df},
            current_value=[],
        )
        tree_component = result["tree_selector_id"]
        option_titles = [node["title"] for node in tree_component.treeData]
        # Options should reflect fresh data: Europe and Asia as top-level groups
        assert "Europe" in option_titles
        assert "Asia" in option_titles
        assert "(Stale selection)" not in option_titles

    def test_call_injects_stale_values(self, tree_filter_pre_built):
        fresh_df = pd.DataFrame({"continent": ["Europe"], "country": ["France"]})
        # "OldCountry" was previously selected but is no longer in the data
        result = tree_filter_pre_built(
            target_to_data_frame={"fig_dynamic": fresh_df},
            current_value=["OldCountry"],
        )
        tree_component = result["tree_selector_id"]
        option_titles = [node["title"] for node in tree_component.treeData]
        assert "(Stale selection)" in option_titles
        stale_node = next(n for n in tree_component.treeData if n["title"] == "(Stale selection)")
        # The stale node's children should include OldCountry
        assert any(child["title"] == "OldCountry" for child in stale_node["children"])

    def test_call_multi_false_stale_string(self, managers_column_hierarchy_dynamic):
        f = vm.Filter(
            column_hierarchy=["continent", "country"],
            targets=["fig_dynamic"],
            selector=vm.TreeSelect(id="tree_selector_id_single", multi=False),
        )
        model_manager["test_page"].controls = [f]
        f.pre_build()
        fresh_df = pd.DataFrame({"continent": ["Europe"], "country": ["France"]})
        result = f(
            target_to_data_frame={"fig_dynamic": fresh_df},
            current_value="Atlantis",
        )
        tree_component = result["tree_selector_id_single"]
        option_titles = [node["title"] for node in tree_component.treeData]
        assert "(Stale selection)" in option_titles

    def test_call_no_stale_when_current_value_empty(self, tree_filter_pre_built):
        fresh_df = pd.DataFrame({"continent": ["Europe"], "country": ["France"]})
        result = tree_filter_pre_built(
            target_to_data_frame={"fig_dynamic": fresh_df},
            current_value=[],
        )
        tree_component = result["tree_selector_id"]
        option_titles = [node["title"] for node in tree_component.treeData]
        assert "(Stale selection)" not in option_titles

    def test_call_target_missing_hierarchy_column_excluded(self, tree_filter_pre_built):
        # DataFrame missing "country" column → silently excluded, options empty
        bad_df = pd.DataFrame({"continent": ["Europe"]})
        result = tree_filter_pre_built(
            target_to_data_frame={"fig_dynamic": bad_df},
            current_value=[],
        )
        tree_component = result["tree_selector_id"]
        assert tree_component.treeData == []

    def test_call_guard_component_is_true(self, tree_filter_pre_built):
        fresh_df = pd.DataFrame({"continent": ["Europe"], "country": ["France"]})
        result = tree_filter_pre_built(
            target_to_data_frame={"fig_dynamic": fresh_df},
            current_value=[],
        )
        guard = result["tree_selector_id_guard_actions_chain"]
        assert guard.data is True
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
hatch run test-unit tests/unit/vizro/models/_controls/test_filter.py::TestFilterCallTree -x -q
```

Expected: FAIL (tree branch not yet in `__call__`)

- [ ] **Step 3: Add `_get_tree_options_dynamic` static method to `Filter`**

In `filter.py`, add this method immediately after `_get_tree_options` (after line ~546):

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

- [ ] **Step 4: Add tree branch in `Filter.__call__`**

In `filter.py`, in the `__call__` method, add `elif _is_tree_selector(selector):` after the `elif _is_numerical_temporal_selector` branch (after line ~209):

```python
        if _is_categorical_selector(selector):
            selector_call_obj = selector(options=self._get_options(targeted_data, current_value))
        elif _is_numerical_temporal_selector(selector):
            _min, _max = self._get_min_max(targeted_data, current_value)
            selector_call_obj = selector(min=_min, max=_max)
        elif _is_tree_selector(selector):
            selector_call_obj = selector(options=self._get_tree_options_dynamic(
                {target: df for target, df in target_to_data_frame.items() if target in self.targets},
                self.column_hierarchy,
                current_value,
            ))
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
hatch run test-unit tests/unit/vizro/models/_controls/test_filter.py::TestFilterCallTree -x -q
```

Expected: 6 tests PASS

- [ ] **Step 6: Run the full filter test suite**

```bash
hatch run test-unit tests/unit/vizro/models/_controls/test_filter.py -x -q
```

Expected: all tests PASS

- [ ] **Step 7: Run the full test suite**

```bash
hatch run test-unit -x -q
```

Expected: all tests PASS

- [ ] **Step 8: Commit**

```bash
git add src/vizro/models/_controls/filter.py tests/unit/vizro/models/_controls/test_filter.py
git commit -m "feat: add _get_tree_options_dynamic and tree branch in Filter.__call__"
```
