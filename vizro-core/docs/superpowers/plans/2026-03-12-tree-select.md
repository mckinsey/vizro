# TreeSelect Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a `vm.TreeSelect` Pydantic model that wraps `fac.AntdTreeSelect` from `feffery-antd-components`, usable as a `Parameter` selector with a simple nested-dict `options` format.

**Architecture:** A single new file `tree_select.py` in the form components directory, following the exact same pattern as `dropdown.py`. Private helpers convert the user-facing nested dict format to the `treeData` format AntdTreeSelect expects. Registered in the same places as all other selectors.

**Tech Stack:** Python, Pydantic v2, Dash, `feffery-antd-components` (`fac.AntdTreeSelect`), `dash-bootstrap-components` (`dbc.Label`), `dash` (`html.Div`, `html.Span`)

---

## Chunk 1: Dependency + helpers + model skeleton

### Task 1: Add feffery-antd-components dependency

**Files:**
- Modify: `vizro-core/pyproject.toml` (dependencies list, lines ~17-34)

- [ ] **Add the dependency**

  In `pyproject.toml`, add `"feffery-antd-components"` to the `dependencies` list after `"python-box"`:

  ```toml
  dependencies = [
    "dash>=4,<5",
    "dash_bootstrap_components>=2",
    "dash-ag-grid>=33.3.3",
    "dash_mantine_components>=2.0.0",
    "pandas>=2",
    "plotly>=5.24.0",
    "pydantic>=2.7.0",
    "flask_caching>=2",
    "wrapt>=1",
    "black",
    "autoflake",
    "packaging",
    "python-box",
    "feffery-antd-components",
  ]
  ```

- [ ] **Verify it installs**

  ```bash
  cd vizro-core && hatch run python -c "import feffery_antd_components as fac; print(fac.__version__)"
  ```

  Expected: prints a version string without error.

- [ ] **Commit**

  ```bash
  git add vizro-core/pyproject.toml
  git commit -m "feat: add feffery-antd-components dependency"
  ```

---

### Task 2: Add TreeOptionsType alias to types.py

**Files:**
- Modify: `vizro-core/src/vizro/models/types.py`

- [ ] **Add the type alias**

  Near the other `TypeAlias` definitions (around line 615), add:

  ```python
  TreeOptionsType: TypeAlias = dict[str, Any]
  ```

  This is just a readable alias — structural validation is done in the model validator.

- [ ] **Verify no import errors**

  ```bash
  cd vizro-core && hatch run python -c "from vizro.models.types import TreeOptionsType; print('ok')"
  ```

  Expected: `ok`

- [ ] **Commit**

  ```bash
  git add vizro-core/src/vizro/models/types.py
  git commit -m "feat: add TreeOptionsType alias to types"
  ```

---

### Task 3: Create tree_select.py with helpers and model

**Files:**
- Create: `vizro-core/src/vizro/models/_components/form/tree_select.py`

- [ ] **Write the file**

  ```python
  from typing import Annotated, Any, Literal

  import dash_bootstrap_components as dbc
  import feffery_antd_components as fac
  from dash import html
  from pydantic import AfterValidator, BeforeValidator, Field, ValidationInfo, model_validator
  from pydantic.json_schema import SkipJsonSchema

  from vizro.models import Tooltip, VizroBaseModel
  from vizro.models._models_utils import _log_call, make_actions_chain
  from vizro.models._tooltip import coerce_str_to_tooltip
  from vizro.models.types import ActionsType, MultiValueType, SingleValueType, TreeOptionsType, _IdProperty


  def _validate_options_structure(options: Any) -> None:
      """Recursively validate that options is a dict of str -> list[str] | dict."""
      if not isinstance(options, dict):
          raise ValueError("options must be a dict.")
      for key, value in options.items():
          if not isinstance(key, str):
              raise ValueError(f"options keys must be strings, got {type(key)}")
          if isinstance(value, list):
              for item in value:
                  if not isinstance(item, str):
                      raise ValueError(f"Leaf values must be strings, got {type(item)}: {item!r}")
          elif isinstance(value, dict):
              _validate_options_structure(value)
          else:
              raise ValueError(
                  f"options values must be list[str] or dict, got {type(value)} for key {key!r}"
              )


  def _convert_options(d: dict | list) -> list[dict]:
      """Convert nested dict options to AntdTreeSelect treeData format."""
      if isinstance(d, list):
          return [{"title": v, "key": v, "value": v} for v in d]
      return [
          {"title": k, "key": k, "value": k, "children": _convert_options(v)}
          for k, v in d.items()
      ]


  def _extract_leaf_keys(d: dict | list) -> set[str]:
      """Recursively collect all leaf string values from the nested dict."""
      if isinstance(d, list):
          return set(d)
      keys: set[str] = set()
      for v in d.values():
          keys |= _extract_leaf_keys(v)
      return keys


  def _validate_multi(multi: bool, info: ValidationInfo) -> bool:
      if "value" not in info.data:
          return multi
      if info.data["value"] and multi is False and isinstance(info.data["value"], list):
          raise ValueError("Please set multi=True if providing a list of default values.")
      return multi


  def _validate_tree_value(value, info: ValidationInfo):
      if "options" not in info.data or not info.data["options"]:
          return value
      leaf_keys = _extract_leaf_keys(info.data["options"])
      if value and not (
          all(v in leaf_keys for v in value) if isinstance(value, list) else value in leaf_keys
      ):
          raise ValueError("Please provide a valid value from `options`.")
      return value


  class TreeSelect(VizroBaseModel):
      """Hierarchical multi/single-option selector.

      Can be provided to [`Parameter`][vizro.models.Parameter].

      """

      type: Literal["tree_select"] = "tree_select"
      options: TreeOptionsType
      value: Annotated[
          SingleValueType | MultiValueType | None,
          AfterValidator(_validate_tree_value),
          Field(default=None, validate_default=True),
      ]
      multi: Annotated[
          bool,
          AfterValidator(_validate_multi),
          Field(default=True, validate_default=True),
      ]
      title: str = Field(default="", description="Title to be displayed")
      description: Annotated[
          Tooltip | None,
          BeforeValidator(coerce_str_to_tooltip),
          Field(default=None),
      ]
      actions: ActionsType = []
      extra: SkipJsonSchema[
          Annotated[
              dict[str, Any],
              Field(
                  default={},
                  description="""Extra keyword arguments passed to `fac.AntdTreeSelect` and overwrite any
  defaults chosen by the Vizro team. This may have unexpected behavior.""",
              ),
          ]
      ]

      @model_validator(mode="before")
      @classmethod
      def _validate_options_structure(cls, data: Any) -> Any:
          if "options" in data and isinstance(data["options"], dict):
              _validate_options_structure(data["options"])
          return data

      @model_validator(mode="after")
      def _make_actions_chain(self):
          return make_actions_chain(self)

      @property
      def _action_triggers(self) -> dict[str, _IdProperty]:
          return {"__default__": f"{self.id}.value"}

      @property
      def _action_outputs(self) -> dict[str, _IdProperty]:
          return {
              "__default__": f"{self.id}.value",
              **({"title": f"{self.id}_title.children"} if self.title else {}),
              **({"description": f"{self.description.id}-text.children"} if self.description else {}),
          }

      @property
      def _action_inputs(self) -> dict[str, _IdProperty]:
          return {"__default__": f"{self.id}.value"}

      def __call__(self):
          tree_data = _convert_options(self.options)
          value = self.value if self.value is not None else ([] if self.multi else None)
          description = self.description.build().children if self.description else [None]

          defaults = {
              "id": self.id,
              "treeData": tree_data,
              "value": value,
              "treeCheckable": self.multi,
              "multiple": self.multi,
              "allowClear": self.multi,
              **( {"showCheckedStrategy": "show-child", "maxTagCount": "responsive"} if self.multi else {} ),
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

      @_log_call
      def build(self):
          return self.__call__()
  ```

- [ ] **Verify the file imports cleanly**

  ```bash
  cd vizro-core && hatch run python -c "from vizro.models._components.form.tree_select import TreeSelect; print('ok')"
  ```

  Expected: `ok`

- [ ] **Commit**

  ```bash
  git add vizro-core/src/vizro/models/_components/form/tree_select.py
  git commit -m "feat: add TreeSelect model"
  ```

---

## Chunk 2: Registration

### Task 4: Register TreeSelect everywhere

**Files:**
- Modify: `vizro-core/src/vizro/models/_components/form/__init__.py`
- Modify: `vizro-core/src/vizro/models/__init__.py`
- Modify: `vizro-core/src/vizro/models/types.py`

- [ ] **Add to form __init__.py**

  Add alongside the other imports and `__all__` entry in `vizro-core/src/vizro/models/_components/form/__init__.py`:

  ```python
  from vizro.models._components.form.tree_select import TreeSelect
  ```

  And add `"TreeSelect"` to the `__all__` list.

- [ ] **Add to models __init__.py**

  In `vizro-core/src/vizro/models/__init__.py`, add the import and `"TreeSelect"` to `__all__`. Follow the same pattern as the other form components.

- [ ] **Add TreeSelect to SelectorType in types.py**

  Find:
  ```python
  SelectorType = Annotated[
      "Checklist | DatePicker | Dropdown | RadioItems | RangeSlider | Slider | Switch",
      Field(discriminator="type", description="Selectors to be used inside a control."),
  ]
  ```

  Change to:
  ```python
  SelectorType = Annotated[
      "Checklist | DatePicker | Dropdown | RadioItems | RangeSlider | Slider | Switch | TreeSelect",
      Field(discriminator="type", description="Selectors to be used inside a control."),
  ]
  ```

- [ ] **Verify full import chain works**

  ```bash
  cd vizro-core && hatch run python -c "import vizro.models as vm; ts = vm.TreeSelect(options={'A': ['x', 'y']}); print(ts)"
  ```

  Expected: prints the TreeSelect model repr without errors.

- [ ] **Commit**

  ```bash
  git add vizro-core/src/vizro/models/_components/form/__init__.py \
          vizro-core/src/vizro/models/__init__.py \
          vizro-core/src/vizro/models/types.py
  git commit -m "feat: register TreeSelect in form, models, and SelectorType"
  ```

---

## Chunk 3: Tests

### Task 5: Write and run tests

**Files:**
- Create: `vizro-core/tests/unit/vizro/models/_components/form/test_tree_select.py`

- [ ] **Write the test file**

  ```python
  import pytest
  from asserts import assert_component_equal
  from dash import html
  import dash_bootstrap_components as dbc
  import feffery_antd_components as fac
  from pydantic import ValidationError

  from vizro.models._components.form import TreeSelect


  SIMPLE_OPTIONS = {"Fruits": ["Apple", "Banana"], "Vegetables": ["Carrot"]}
  NESTED_OPTIONS = {
      "Electronics": {
          "Phones": ["iPhone", "Android"],
          "Laptops": ["MacBook"],
      }
  }


  class TestTreeSelectInstantiation:
      def test_defaults(self):
          ts = TreeSelect(options=SIMPLE_OPTIONS)
          assert ts.type == "tree_select"
          assert ts.multi is True
          assert ts.value is None
          assert ts.title == ""
          assert ts.description is None
          assert ts.actions == []
          assert ts.extra == {}

      def test_options_required(self):
          with pytest.raises(ValidationError):
              TreeSelect()

      def test_valid_flat_options(self):
          ts = TreeSelect(options={"A": ["x", "y"]})
          assert ts.options == {"A": ["x", "y"]}

      def test_valid_nested_options(self):
          ts = TreeSelect(options=NESTED_OPTIONS)
          assert ts.options == NESTED_OPTIONS

      def test_empty_options(self):
          ts = TreeSelect(options={})
          assert ts.options == {}

      def test_invalid_options_not_dict(self):
          with pytest.raises(ValidationError, match="options must be a dict"):
              TreeSelect(options=["a", "b"])

      def test_invalid_options_non_string_leaf(self):
          with pytest.raises(ValidationError, match="Leaf values must be strings"):
              TreeSelect(options={"A": [1, 2]})

      def test_invalid_options_invalid_value_type(self):
          with pytest.raises(ValidationError):
              TreeSelect(options={"A": 42})

      def test_valid_value(self):
          ts = TreeSelect(options=SIMPLE_OPTIONS, value=["Apple"])
          assert ts.value == ["Apple"]

      def test_valid_value_nested(self):
          ts = TreeSelect(options=NESTED_OPTIONS, value=["iPhone", "MacBook"])
          assert ts.value == ["iPhone", "MacBook"]

      def test_invalid_value_not_in_options(self):
          with pytest.raises(ValidationError, match="valid value from `options`"):
              TreeSelect(options=SIMPLE_OPTIONS, value=["NotAFruit"])

      def test_multi_false_with_single_value(self):
          ts = TreeSelect(options=SIMPLE_OPTIONS, value="Apple", multi=False)
          assert ts.value == "Apple"

      def test_multi_false_with_list_value_raises(self):
          with pytest.raises(ValidationError, match="multi=True"):
              TreeSelect(options=SIMPLE_OPTIONS, value=["Apple"], multi=False)


  class TestTreeSelectBuild:
      def test_build_returns_div(self):
          ts = TreeSelect(options=SIMPLE_OPTIONS)
          result = ts.build()
          assert isinstance(result, html.Div)

      def test_build_no_title(self):
          ts = TreeSelect(options=SIMPLE_OPTIONS)
          result = ts.build()
          # First child is None when no title
          assert result.children[0] is None

      def test_build_with_title(self):
          ts = TreeSelect(options=SIMPLE_OPTIONS, title="Pick a fruit")
          result = ts.build()
          assert isinstance(result.children[0], dbc.Label)

      def test_build_antd_component(self):
          ts = TreeSelect(options=SIMPLE_OPTIONS)
          result = ts.build()
          antd = result.children[1]
          assert isinstance(antd, fac.AntdTreeSelect)
          assert antd.id == ts.id
          assert antd.treeCheckable is True
          assert antd.multiple is True
          assert antd.allowClear is True
          assert antd.showCheckedStrategy == "show-child"
          assert antd.maxTagCount == "responsive"

      def test_build_multi_false(self):
          ts = TreeSelect(options=SIMPLE_OPTIONS, multi=False)
          result = ts.build()
          antd = result.children[1]
          assert antd.treeCheckable is False
          assert antd.multiple is False
          assert antd.allowClear is False
          assert not hasattr(antd, "showCheckedStrategy") or antd.showCheckedStrategy is None

      def test_build_default_value_multi_true(self):
          ts = TreeSelect(options=SIMPLE_OPTIONS)
          result = ts.build()
          antd = result.children[1]
          assert antd.value == []

      def test_build_default_value_multi_false(self):
          ts = TreeSelect(options=SIMPLE_OPTIONS, multi=False)
          result = ts.build()
          antd = result.children[1]
          assert antd.value is None

      def test_build_with_value(self):
          ts = TreeSelect(options=SIMPLE_OPTIONS, value=["Apple"])
          result = ts.build()
          antd = result.children[1]
          assert antd.value == ["Apple"]

      def test_build_extra_overrides(self):
          ts = TreeSelect(options=SIMPLE_OPTIONS, extra={"listHeight": 500})
          result = ts.build()
          antd = result.children[1]
          assert antd.listHeight == 500

      def test_convert_options_flat(self):
          from vizro.models._components.form.tree_select import _convert_options
          result = _convert_options({"A": ["x", "y"]})
          assert result == [
              {"title": "A", "key": "A", "value": "A", "children": [
                  {"title": "x", "key": "x", "value": "x"},
                  {"title": "y", "key": "y", "value": "y"},
              ]}
          ]

      def test_convert_options_nested(self):
          from vizro.models._components.form.tree_select import _convert_options
          result = _convert_options({"A": {"B": ["x"]}})
          assert result == [
              {"title": "A", "key": "A", "value": "A", "children": [
                  {"title": "B", "key": "B", "value": "B", "children": [
                      {"title": "x", "key": "x", "value": "x"},
                  ]}
              ]}
          ]

      def test_extract_leaf_keys(self):
          from vizro.models._components.form.tree_select import _extract_leaf_keys
          result = _extract_leaf_keys(NESTED_OPTIONS)
          assert result == {"iPhone", "Android", "MacBook"}
  ```

- [ ] **Run the tests**

  ```bash
  cd vizro-core && hatch run test-unit tests/unit/vizro/models/_components/form/test_tree_select.py -v
  ```

  Expected: all tests pass.

- [ ] **Run the full form test suite to check for regressions**

  ```bash
  cd vizro-core && hatch run test-unit tests/unit/vizro/models/_components/form/ -v
  ```

  Expected: all tests pass.

- [ ] **Commit**

  ```bash
  git add vizro-core/tests/unit/vizro/models/_components/form/test_tree_select.py
  git commit -m "test: add TreeSelect unit tests"
  ```

---

### Task 6: Run lint

- [ ] **Run lint and fix any issues**

  ```bash
  cd vizro-core && hatch run lint
  ```

  Expected: no errors. If there are auto-fixable issues, lint will fix them in place — just re-run to confirm clean.

- [ ] **Commit any lint fixes**

  ```bash
  git add -u
  git commit -m "style: lint fixes for TreeSelect"
  ```
  (Only needed if lint made changes.)
