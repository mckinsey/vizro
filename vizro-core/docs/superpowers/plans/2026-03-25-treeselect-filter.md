# TreeSelect Filter Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extend `vm.Filter` to accept `column_hierarchy=["continent", "country", "city"]`, automatically build a `TreeSelect` with hierarchical options from the DataFrame, and filter on the leaf column.

**Architecture:** A new `column_hierarchy` field on `Filter` triggers a separate `if self.column_hierarchy:` branch in `pre_build` that builds a wide DataFrame from all targeted figures, constructs the nested dict options, and sets up a `TreeSelect` selector. `TreeSelect` gains an optional `options` default and a duplicate-leaf validator. All existing `column: str` behaviour is completely unchanged in an `else:` branch.

**Tech Stack:** Python, Pydantic v2, pandas, vizro-core. Tests run with `hatch run test-unit` from `vizro-core/`. Lint with `hatch run lint`.

**Spec:** `docs/superpowers/specs/2026-03-25-treeselect-filter-design.md`

**Important pattern for filter tests:** Every test that calls `filter.pre_build()` must first attach the filter to the page via `model_manager["test_page"].controls = [filter]`. This is because `pre_build` calls `check_control_targets(control=self)` which verifies the filter is in a page's controls. See existing tests at `tests/unit/vizro/models/_controls/test_filter.py:636` for the pattern.

**Important note on `column: Optional[str] = None`:** `_action_outputs`, `_action_triggers`, and `_action_inputs` properties on `Filter` use `self.selector` which is `None` until `pre_build` runs. These properties are only ever accessed after `pre_build` in Vizro's build pipeline, so `column` being `None` at construction time is safe.

---

## File Map

| File | Change |
|------|--------|
| `src/vizro/models/_components/form/tree_select.py` | Make `options` optional; add `_check_no_duplicate_leaves`; update `_validate_options_structure` model validator; add `options` param to `__call__`; update docstring |
| `src/vizro/models/_controls/_controls_utils.py` | Import `TreeSelect`; add `_is_tree_selector`; update `get_selector_default_value` |
| `src/vizro/models/_controls/filter.py` | Make `column` optional; add `column_hierarchy` field; add model validator; add `_get_tree_options`; update `pre_build` |
| `tests/unit/vizro/models/_components/form/test_tree_select.py` | Update `test_options_required` → `test_create_tree_select_no_args`; add duplicate-leaf and `__call__` tests |
| `tests/unit/vizro/models/_controls/test_filter.py` | Add hierarchy fixture, `TestGetSelectorDefaultValueTreeSelect`, `TestGetTreeOptions`, `TestFilterColumnHierarchyValidation`, `TestFilterHierarchyPreBuild` |

---

## Task 1: Make `TreeSelect.options` optional and add `_check_no_duplicate_leaves`

**Files:**
- Modify: `src/vizro/models/_components/form/tree_select.py`
- Test: `tests/unit/vizro/models/_components/form/test_tree_select.py`

- [ ] **Step 1: Write the failing tests**

In `test_tree_select.py`:
- **Delete** the existing `test_options_required` test (lines 55–57) — after this task, `TreeSelect()` will be valid so it would become a false negative.
- The existing `test_empty_options` test (which tests `TreeSelect(options={})`) is retained as-is since it tests explicit empty-dict passing; the new `test_create_tree_select_no_args` tests the no-argument default.
- Add `test_create_tree_select_no_args` and `test_duplicate_leaf_values_raises` to `TestTreeSelectInstantiation`:

```python
def test_create_tree_select_no_args(self):
    ts = TreeSelect()
    assert ts.options == {}
    assert ts.value is None

def test_duplicate_leaf_values_raises(self):
    with pytest.raises(ValidationError, match="Duplicate leaf values"):
        TreeSelect(options={"France": ["Bruges"], "Belgium": ["Bruges"]})
```

Add a new test class at the end of the file:

```python
class TestTreeSelectCall:
    def test_call_with_options_param_overrides_self_options(self):
        ts = TreeSelect(options={"A": ["x"]})
        result = ts(options={"B": ["y"]})
        # title is "" (falsy) so children[0] is None, children[1] is AntdTreeSelect
        tree_select_component = result.children[1]
        assert tree_select_component.treeData == [
            {"title": "B", "key": "B", "value": "B", "children": [
                {"title": "y", "key": "y", "value": "y"}
            ]}
        ]

    def test_call_without_options_param_uses_self_options(self):
        ts = TreeSelect(options={"A": ["x"]})
        result = ts()
        # title is "" (falsy) so children[0] is None, children[1] is AntdTreeSelect
        tree_select_component = result.children[1]
        assert tree_select_component.treeData == [
            {"title": "A", "key": "A", "value": "A", "children": [
                {"title": "x", "key": "x", "value": "x"}
            ]}
        ]
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd vizro-core && hatch run test-unit tests/unit/vizro/models/_components/form/test_tree_select.py::TestTreeSelectInstantiation::test_create_tree_select_no_args tests/unit/vizro/models/_components/form/test_tree_select.py::TestTreeSelectInstantiation::test_duplicate_leaf_values_raises tests/unit/vizro/models/_components/form/test_tree_select.py::TestTreeSelectCall -v
```

Expected: `test_create_tree_select_no_args` FAIL (options required), `test_duplicate_leaf_values_raises` FAIL (no such validation), `TestTreeSelectCall` FAIL.

- [ ] **Step 3: Implement changes in `tree_select.py`**

**3a.** Add `_check_no_duplicate_leaves` standalone function after `_extract_leaf_keys`:

```python
def _check_no_duplicate_leaves(options: dict[Any, Any]) -> None:
    """Raise ValueError if any leaf value appears more than once across branches."""
    all_leaves: list[str] = []

    def _collect_leaves(d: dict[Any, Any] | list[Any]) -> None:
        if isinstance(d, list):
            all_leaves.extend(d)
        else:
            for v in d.values():
                _collect_leaves(v)

    _collect_leaves(options)
    seen: set[str] = set()
    duplicates: set[str] = set()
    for leaf in all_leaves:
        if leaf in seen:
            duplicates.add(leaf)
        seen.add(leaf)
    if duplicates:
        raise ValueError(f"Duplicate leaf values found in options: {duplicates!r}")
```

**3b.** Update `_validate_options_structure` model validator to also call `_check_no_duplicate_leaves` when options is non-empty.

**Important naming note:** Inside the class method body, the unqualified name `_validate_options_structure(data["options"])` resolves to the **module-level function** of the same name — not to `cls._validate_options_structure`. This is intentional name shadowing and works correctly. Do NOT change it to `cls._validate_options_structure(...)` which would cause infinite recursion.

```python
@model_validator(mode="before")
@classmethod
def _validate_options_structure(cls, data: Any) -> Any:
    if "options" in data and isinstance(data["options"], dict):
        _validate_options_structure(data["options"])  # calls the module-level function
        if data["options"]:  # skip check for empty dict
            _check_no_duplicate_leaves(data["options"])
    return data
```

**3c.** Change `options` field to have a default of `{}`:

```python
options: TreeOptionsType = Field(default={})
```

**3d.** Update `__call__` to accept optional `options` param:

```python
def __call__(self, options=None):
    tree_data = _convert_options(options if options is not None else self.options)
    value = self.value if self.value is not None else ([] if self.multi else None)
    description = self.description.build().children if self.description else [None]

    defaults = {
        "id": self.id,
        "treeData": tree_data,
        "value": value,
        "treeCheckable": self.multi,
        "multiple": self.multi,
        "allowClear": self.multi,
        **({"showCheckedStrategy": "show-child", "maxTagCount": "responsive"} if self.multi else {}),
        "listHeight": 300,
        "locale": "en-us",
        "persistence": True,
        "persistence_type": "session",
        "placeholder": "Select option",
    }

    return html.Div(
        children=[
            dbc.Label(
                children=[html.Span(id=f"{self.id}_title", children=self.title), *description],
                html_for=self.id,
            )
            if self.title
            else None,
            fac.AntdTreeSelect(**(defaults | self.extra)),
        ]
    )
```

**3e.** Update `TreeSelect` docstring to mention `Filter`:

```python
class TreeSelect(VizroBaseModel):
    """Hierarchical multi/single-option selector.

    Can be provided to [`Filter`][vizro.models.Filter] or [`Parameter`][vizro.models.Parameter].

    """
```

- [ ] **Step 4: Run the new tests to verify they pass**

```bash
hatch run test-unit tests/unit/vizro/models/_components/form/test_tree_select.py -v
```

Expected: all pass.

- [ ] **Step 5: Lint**

```bash
hatch run lint
```

- [ ] **Step 6: Commit**

```bash
git add src/vizro/models/_components/form/tree_select.py tests/unit/vizro/models/_components/form/test_tree_select.py
git commit -m "feat: make TreeSelect.options optional and add duplicate-leaf validation"
```

---

## Task 2: Update `_controls_utils.py` to support `TreeSelect`

**Files:**
- Modify: `src/vizro/models/_controls/_controls_utils.py`
- Test: `tests/unit/vizro/models/_controls/test_filter.py`

- [ ] **Step 1: Write the failing tests**

Add to `test_filter.py` (near the top with other imports, add `from vizro.models._controls._controls_utils import get_selector_default_value` and `from vizro.models._components.form import TreeSelect`). Add a new class:

```python
class TestGetSelectorDefaultValueTreeSelect:
    def test_tree_select_multi_true_default_is_empty_list(self):
        ts = TreeSelect(multi=True)
        assert get_selector_default_value(ts) == []

    def test_tree_select_multi_false_default_is_none(self):
        ts = TreeSelect(multi=False)
        assert get_selector_default_value(ts) is None

    def test_tree_select_with_value_returns_value(self):
        # This test passes BEFORE the new branch is added (early-return handles it),
        # but it documents the expected contract so is worth keeping.
        ts = TreeSelect(options={"A": ["x"]}, value=["x"])
        assert get_selector_default_value(ts) == ["x"]
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
hatch run test-unit tests/unit/vizro/models/_controls/test_filter.py::TestGetSelectorDefaultValueTreeSelect -v
```

Expected: `test_tree_select_multi_true_default_is_empty_list` FAIL — currently returns `None`.

- [ ] **Step 3: Implement the changes in `_controls_utils.py`**

**3a.** Add `TreeSelect` to imports:

```python
from vizro.models import (
    Checklist,
    Container,
    DatePicker,
    Dropdown,
    RadioItems,
    RangeSlider,
    Slider,
    Switch,
    TreeSelect,
    VizroBaseModel,
)
```

**3b.** Add `_is_tree_selector` after `_is_boolean_selector`:

```python
def _is_tree_selector(x: object) -> TypeIs[TreeSelect]:
    return isinstance(x, TreeSelect)
```

**3c.** Update `get_selector_default_value` to handle `TreeSelect` — add a branch before the implicit `return None` at the end:

```python
def get_selector_default_value(selector: SelectorType) -> Any:
    """Get default value for a selector if not explicitly provided.
    ...
    """
    if selector.value is not None:
        return selector.value

    if _is_numerical_temporal_selector(selector):
        is_range = isinstance(selector, RangeSlider) or getattr(selector, "range", False)
        return [selector.min, selector.max] if is_range else selector.min
    elif _is_categorical_selector(selector):
        is_multi = isinstance(selector, Checklist) or getattr(selector, "multi", False)
        _, default_value = get_dict_options_and_default(options=selector.options, multi=is_multi)
        return default_value
    elif _is_tree_selector(selector):
        return [] if selector.multi else None
    # Boolean selectors always have a default value specified so no need to handle them here.
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
hatch run test-unit tests/unit/vizro/models/_controls/test_filter.py::TestGetSelectorDefaultValueTreeSelect -v
```

Expected: all pass.

- [ ] **Step 5: Lint**

```bash
hatch run lint
```

- [ ] **Step 6: Commit**

```bash
git add src/vizro/models/_controls/_controls_utils.py tests/unit/vizro/models/_controls/test_filter.py
git commit -m "feat: add TreeSelect support to _controls_utils"
```

---

## Task 3: Extend `Filter` with `column_hierarchy` field and model validator

**Files:**
- Modify: `src/vizro/models/_controls/filter.py`
- Test: `tests/unit/vizro/models/_controls/test_filter.py`

This task adds the new field and validator only — `pre_build` changes come in Task 4.

- [ ] **Step 1: Write the failing tests**

Add to `test_filter.py`:

```python
class TestFilterColumnHierarchyValidation:
    def test_both_column_and_column_hierarchy_raises(self):
        with pytest.raises(ValidationError, match="Only one of"):
            vm.Filter(column="species", column_hierarchy=["a", "b"])

    def test_neither_column_nor_column_hierarchy_raises(self):
        with pytest.raises(ValidationError, match="One of"):
            vm.Filter()

    def test_column_hierarchy_sets_field(self):
        f = vm.Filter(column_hierarchy=["continent", "country", "city"])
        assert f.column_hierarchy == ["continent", "country", "city"]
        # column is None at construction; set to column_hierarchy[-1] in pre_build
        assert f.column is None

    def test_column_alone_still_works(self):
        f = vm.Filter(column="species")
        assert f.column == "species"
        assert f.column_hierarchy == []
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
hatch run test-unit tests/unit/vizro/models/_controls/test_filter.py::TestFilterColumnHierarchyValidation -v
```

Expected: all fail — `column` is still required and `column_hierarchy` doesn't exist yet.

- [ ] **Step 3: Implement field and validator changes in `filter.py`**

**3a.** Add `Optional` to the `typing` import:

```python
from typing import Any, Iterable, Literal, Optional, cast
```

**3b.** Add `TreeSelect` and `_check_no_duplicate_leaves` to imports:

```python
from vizro.models._components.form import Checklist, DatePicker, Dropdown, RangeSlider, Switch, TreeSelect
from vizro.models._components.form.tree_select import _check_no_duplicate_leaves
```

**3c.** Change `column` field and add `column_hierarchy` field (replace the existing `column` field):

```python
column: Optional[str] = Field(
    default=None,
    description="Column of DataFrame to filter. Exactly one of `column` or `column_hierarchy` must be set.",
)
column_hierarchy: list[str] = Field(
    default=[],
    description="Ordered list of DataFrame columns forming a hierarchy for TreeSelect. "
    "Exactly one of `column` or `column_hierarchy` must be set.",
)
```

**3d.** Add `check_column_or_hierarchy` model validator (insert before `check_id_set_for_url_control`):

```python
@model_validator(mode="before")
@classmethod
def check_column_or_hierarchy(cls, data: Any) -> Any:
    # mode="before" can receive non-dict input (e.g. a model instance); guard against that.
    if not isinstance(data, dict):
        return data
    has_column = bool(data.get("column"))
    has_hierarchy = bool(data.get("column_hierarchy"))
    if has_column and has_hierarchy:
        raise ValueError("Only one of `column` or `column_hierarchy` can be set.")
    if not has_column and not has_hierarchy:
        raise ValueError("One of `column` or `column_hierarchy` must be set.")
    return data
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
hatch run test-unit tests/unit/vizro/models/_controls/test_filter.py::TestFilterColumnHierarchyValidation -v
```

Expected: all pass.

- [ ] **Step 5: Run full filter test suite to check no regressions**

```bash
hatch run test-unit tests/unit/vizro/models/_controls/test_filter.py -v
```

Expected: all existing tests still pass.

- [ ] **Step 6: Lint**

```bash
hatch run lint
```

- [ ] **Step 7: Commit**

```bash
git add src/vizro/models/_controls/filter.py tests/unit/vizro/models/_controls/test_filter.py
git commit -m "feat: add column_hierarchy field and model validator to Filter"
```

---

## Task 4: Implement `Filter._get_tree_options` and the `pre_build` hierarchy branch

**Files:**
- Modify: `src/vizro/models/_controls/filter.py`
- Test: `tests/unit/vizro/models/_controls/test_filter.py`

- [ ] **Step 1: Write the failing tests for `_get_tree_options`**

Add to `test_filter.py`:

```python
class TestGetTreeOptions:
    def test_three_level_hierarchy(self):
        wide_df = pd.DataFrame({
            "continent": ["Americas", "Europe", "Europe", "Europe"],
            "country": ["USA", "France", "France", "Germany"],
            "city": ["New York", "Lyon", "Paris", "Berlin"],
        })
        result = Filter._get_tree_options(wide_df, ["continent", "country", "city"])
        assert result == {
            "Americas": {"USA": ["New York"]},
            "Europe": {
                "France": ["Lyon", "Paris"],  # sorted alphabetically
                "Germany": ["Berlin"],
            },
        }

    def test_two_level_hierarchy(self):
        wide_df = pd.DataFrame({
            "continent": ["Americas", "Europe", "Europe"],
            "city": ["New York", "Lyon", "Paris"],
        })
        result = Filter._get_tree_options(wide_df, ["continent", "city"])
        assert result == {
            "Americas": ["New York"],
            "Europe": ["Lyon", "Paris"],
        }

    def test_duplicate_rows_deduplicated(self):
        # Simulate two figures with overlapping rows
        wide_df = pd.DataFrame({
            "continent": ["Europe", "Europe", "Europe"],
            "country": ["France", "France", "Germany"],
            "city": ["Paris", "Paris", "Berlin"],  # Paris appears twice
        })
        result = Filter._get_tree_options(wide_df, ["continent", "country", "city"])
        assert result == {
            "Europe": {
                "France": ["Paris"],  # deduped
                "Germany": ["Berlin"],
            },
        }
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
hatch run test-unit tests/unit/vizro/models/_controls/test_filter.py::TestGetTreeOptions -v
```

Expected: `AttributeError: type object 'Filter' has no attribute '_get_tree_options'`.

- [ ] **Step 3: Implement `_get_tree_options` in `filter.py`**

Add as a static method on `Filter` (after `_get_options`):

```python
@staticmethod
def _get_tree_options(wide_df: pd.DataFrame, columns: list[str]) -> dict[str, Any]:
    """Build a nested dict of options from a wide DataFrame with one column per hierarchy level."""
    wide_df = wide_df[columns].drop_duplicates()

    def _build_nested(df: pd.DataFrame, remaining_columns: list[str]) -> dict | list:
        col = remaining_columns[0]
        rest = remaining_columns[1:]
        if not rest:
            return sorted(df[col].unique().tolist())
        return {
            key: _build_nested(group, rest)
            for key, group in df.groupby(col, sort=True)
        }

    return _build_nested(wide_df, columns)
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
hatch run test-unit tests/unit/vizro/models/_controls/test_filter.py::TestGetTreeOptions -v
```

Expected: all pass.

- [ ] **Step 5: Write failing integration tests for the `pre_build` hierarchy path**

First add a hierarchy fixture to `test_filter.py` (at module level, alongside existing fixtures). Note: `model_manager["test_page"].controls = [filter]` must be called in each test before `filter.pre_build()`, matching the existing pattern.

```python
@pytest.fixture
def managers_column_hierarchy():
    """Page with two graphs sharing continent/country/city columns."""
    df1 = pd.DataFrame({
        "continent": ["Europe", "Europe", "Americas"],
        "country": ["France", "France", "USA"],
        "city": ["Paris", "Lyon", "New York"],
    })
    df2 = pd.DataFrame({
        "continent": ["Europe", "Asia"],
        "country": ["Germany", "Japan"],
        "city": ["Berlin", "Tokyo"],
    })
    vm.Page(
        id="test_page",
        title="Page Title",
        components=[
            vm.Graph(id="fig_1", figure=px.scatter(df1, x="city", y="city")),
            vm.Graph(id="fig_2", figure=px.scatter(df2, x="city", y="city")),
        ],
    )
    Vizro._pre_build()
```

Then add the test class:

```python
class TestFilterHierarchyPreBuild:
    def test_default_selector_is_tree_select(self, managers_column_hierarchy):
        from vizro.models._components.form import TreeSelect
        f = vm.Filter(column_hierarchy=["continent", "country", "city"])
        model_manager["test_page"].controls = [f]
        f.pre_build()
        assert isinstance(f.selector, TreeSelect)

    def test_column_set_to_leaf(self, managers_column_hierarchy):
        f = vm.Filter(column_hierarchy=["continent", "country", "city"])
        model_manager["test_page"].controls = [f]
        f.pre_build()
        assert f.column == "city"

    def test_title_defaults_to_leaf_column_name(self, managers_column_hierarchy):
        f = vm.Filter(column_hierarchy=["continent", "country", "city"])
        model_manager["test_page"].controls = [f]
        f.pre_build()
        assert f.selector.title == "City"

    def test_options_built_from_data(self, managers_column_hierarchy):
        f = vm.Filter(column_hierarchy=["continent", "country", "city"])
        model_manager["test_page"].controls = [f]
        f.pre_build()
        options = f.selector.options
        assert "Europe" in options
        assert "France" in options["Europe"]
        assert "Paris" in options["Europe"]["France"]
        assert "Berlin" in options["Europe"]["Germany"]
        assert "Tokyo" in options["Asia"]

    def test_custom_tree_select_config_respected(self, managers_column_hierarchy):
        from vizro.models._components.form import TreeSelect
        f = vm.Filter(
            column_hierarchy=["continent", "country", "city"],
            selector=vm.TreeSelect(multi=False, title="Location"),
        )
        model_manager["test_page"].controls = [f]
        f.pre_build()
        assert f.selector.multi is False
        assert f.selector.title == "Location"

    def test_non_tree_select_selector_raises(self, managers_column_hierarchy):
        f = vm.Filter(
            column_hierarchy=["continent", "country", "city"],
            selector=vm.Dropdown(),
        )
        model_manager["test_page"].controls = [f]
        with pytest.raises(ValueError, match="TreeSelect"):
            f.pre_build()

    def test_duplicate_leaf_values_in_data_raises(self):
        # This test creates its own page inline (not using managers_column_hierarchy fixture)
        # because it needs specific data. The conftest autouse fixture clears model_manager
        # between tests, so this is safe even with a fresh page ID.
        df = pd.DataFrame({
            "continent": ["Europe", "Europe"],
            "country": ["France", "Belgium"],
            "city": ["Bruges", "Bruges"],
        })
        vm.Page(
            id="test_page_dup",
            title="Page",
            components=[vm.Graph(id="fig_dup", figure=px.scatter(df, x="city", y="city"))],
        )
        Vizro._pre_build()
        f = vm.Filter(column_hierarchy=["continent", "country", "city"])
        model_manager["test_page_dup"].controls = [f]
        with pytest.raises(ValueError, match="Duplicate leaf values"):
            f.pre_build()

    def test_figure_missing_intermediate_column_excluded(self):
        # This test creates its own page inline for the same reason as above.
        df_full = pd.DataFrame({"continent": ["Europe"], "country": ["France"], "city": ["Paris"]})
        df_missing = pd.DataFrame({"continent": ["Asia"], "city": ["Tokyo"]})  # no "country"
        vm.Page(
            id="test_page_missing",
            title="Page",
            components=[
                vm.Graph(id="fig_full", figure=px.scatter(df_full, x="city", y="city")),
                vm.Graph(id="fig_missing", figure=px.scatter(df_missing, x="city", y="city")),
            ],
        )
        Vizro._pre_build()
        f = vm.Filter(column_hierarchy=["continent", "country", "city"])
        model_manager["test_page_missing"].controls = [f]
        f.pre_build()
        assert "fig_full" in f.targets
        assert "fig_missing" not in f.targets

    def test_filter_action_uses_leaf_column(self, managers_column_hierarchy):
        f = vm.Filter(column_hierarchy=["continent", "country", "city"])
        model_manager["test_page"].controls = [f]
        f.pre_build()
        # f.selector.actions[0] is a _filter action instance with a .column field
        assert f.selector.actions[0].column == "city"
```

- [ ] **Step 6: Run tests to verify they fail**

```bash
hatch run test-unit tests/unit/vizro/models/_controls/test_filter.py::TestFilterHierarchyPreBuild -v
```

Expected: all fail.

- [ ] **Step 7: Implement the hierarchy branch in `Filter.pre_build`**

Restructure `pre_build` in `filter.py` so that hierarchy logic is in `if self.column_hierarchy:` and all existing code is in `else:`. Capture the user's original `self.targets` before overwriting, to correctly decide whether to raise on a missing-column target.

```python
@_log_call
def pre_build(self):
    check_control_targets(control=self)

    if self.column_hierarchy:
        # Step 1: set leaf column immediately — required before _validate_targeted_data
        self.column = self.column_hierarchy[-1]
        user_provided_targets = list(self.targets)  # capture before overwriting

        proposed_targets = self.targets or [
            model.id
            for model in cast(
                Iterable[FigureType], model_manager._get_models(FIGURE_MODELS, get_control_parent(control=self))
            )
        ]

        multi_data_source_name_load_kwargs: list[tuple[DataSourceName, dict[str, Any]]] = [
            (cast(FigureType, model_manager[target])["data_frame"], {}) for target in proposed_targets
        ]
        target_to_data_frame = dict(
            zip(proposed_targets, data_manager._multi_load(multi_data_source_name_load_kwargs))
        )

        # Validate leaf column exists in each figure — establishes initial target set
        targeted_data = self._validate_targeted_data(
            target_to_data_frame, eagerly_raise_column_not_found_error=bool(user_provided_targets)
        )
        self.targets = list(targeted_data.columns)

        # Validate all hierarchy columns exist; exclude or raise for figures missing any
        validated_targets = []
        for target in self.targets:
            df = target_to_data_frame[target]
            missing = [col for col in self.column_hierarchy if col not in df.columns]
            if missing:
                if bool(user_provided_targets):
                    raise ValueError(
                        f"Target {target} is missing hierarchy columns {missing} in its DataFrame."
                    )
                # silently exclude figures that don't have all hierarchy columns
            else:
                validated_targets.append(target)
        self.targets = validated_targets

        # Build wide_df from validated targets
        dfs = [target_to_data_frame[target][self.column_hierarchy] for target in self.targets]
        wide_df = pd.concat(dfs, ignore_index=True).drop_duplicates()

        # Validate selector type — TreeSelect is the only allowed selector
        if self.selector is not None and not isinstance(self.selector, TreeSelect):
            raise ValueError(
                f"column_hierarchy can only be used with a TreeSelect selector, "
                f"got {type(self.selector).__name__}."
            )
        self.selector = self.selector or TreeSelect()

        self._column_type = "categorical"
        self.selector.title = self.selector.title or self.column.title()

        # Build options if not user-supplied; validate for duplicate leaves
        if not self.selector.options:
            built_options = self._get_tree_options(wide_df, self.column_hierarchy)
            _check_no_duplicate_leaves(built_options)
            self.selector.options = built_options

        self.selector.value = get_selector_default_value(self.selector)

        # Dynamic detection is naturally skipped: options is now non-empty so the condition
        # `not getattr(self.selector, "options", [])` is False.
        # TODO: add dynamic support for column_hierarchy

        if not self.selector.actions:
            self.selector.actions = [
                _filter(
                    id=f"{FILTER_ACTION_PREFIX}_{self.id}",
                    column=self.column,
                    filter_function=_filter_isin,
                    targets=self.targets,
                ),
            ]

        if selector_inner_component_properties := getattr(self.selector, "_inner_component_properties", None):
            self._selector_properties = set(selector_inner_component_properties) - set(html.Div().available_properties)

    else:
        # Existing standard path — completely unchanged
        proposed_targets = self.targets or [
            model.id
            for model in cast(
                Iterable[FigureType], model_manager._get_models(FIGURE_MODELS, get_control_parent(control=self))
            )
        ]

        multi_data_source_name_load_kwargs: list[tuple[DataSourceName, dict[str, Any]]] = [
            (cast(FigureType, model_manager[target])["data_frame"], {}) for target in proposed_targets
        ]

        target_to_data_frame = dict(zip(proposed_targets, data_manager._multi_load(multi_data_source_name_load_kwargs)))
        targeted_data = self._validate_targeted_data(
            target_to_data_frame, eagerly_raise_column_not_found_error=bool(self.targets)
        )
        self.targets = list(targeted_data.columns)

        self._column_type = self._validate_column_type(targeted_data)
        self.selector = self.selector or DEFAULT_SELECTORS[self._column_type]()
        self.selector.title = self.selector.title or self.column.title()

        if isinstance(self.selector, DISALLOWED_SELECTORS.get(self._column_type, ())):
            raise ValueError(
                f"Chosen selector {type(self.selector).__name__} is not compatible with {self._column_type} column "
                f"'{self.column}'."
            )

        if (
            not _is_boolean_selector(self.selector)
            and not getattr(self.selector, "options", [])
            and getattr(self.selector, "min", None) is None
            and getattr(self.selector, "max", None) is None
        ):
            for target_id in self.targets:
                data_source_name = cast(FigureType, model_manager[target_id])["data_frame"]
                if isinstance(data_manager[data_source_name], _DynamicData):
                    self._dynamic = True
                    self.selector._dynamic = True
                    break

        if _is_numerical_temporal_selector(self.selector):
            _min, _max = self._get_min_max(targeted_data)
            if self.selector.min is None:
                self.selector.min = _min
            if self.selector.max is None:
                self.selector.max = _max
        elif _is_categorical_selector(self.selector):
            self.selector.options = self.selector.options or self._get_options(targeted_data)

        self.selector.value = get_selector_default_value(self.selector)

        if not self.selector.actions:
            if isinstance(self.selector, RangeSlider) or (
                isinstance(self.selector, DatePicker) and self.selector.range
            ):
                filter_function = _filter_between
            else:
                filter_function = _filter_isin

            self.selector.actions = [
                _filter(
                    id=f"{FILTER_ACTION_PREFIX}_{self.id}",
                    column=self.column,
                    filter_function=filter_function,
                    targets=self.targets,
                ),
            ]

        if selector_inner_component_properties := getattr(self.selector, "_inner_component_properties", None):
            self._selector_properties = set(selector_inner_component_properties) - set(html.Div().available_properties)
```

- [ ] **Step 8: Run hierarchy tests to verify they pass**

```bash
hatch run test-unit tests/unit/vizro/models/_controls/test_filter.py::TestFilterHierarchyPreBuild -v
```

Expected: all pass.

- [ ] **Step 9: Run full filter test suite to verify no regressions**

```bash
hatch run test-unit tests/unit/vizro/models/_controls/test_filter.py -v
```

Expected: all pass.

- [ ] **Step 10: Run complete unit test suite**

```bash
hatch run test-unit
```

Expected: all pass, no regressions.

- [ ] **Step 11: Lint**

```bash
hatch run lint
```

- [ ] **Step 12: Commit**

```bash
git add src/vizro/models/_controls/filter.py tests/unit/vizro/models/_controls/test_filter.py
git commit -m "feat: implement column_hierarchy support in Filter.pre_build"
```
