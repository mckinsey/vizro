# TreeSelect Component Design

**Date:** 2026-03-12
**Status:** Reviewed

## Overview

Add a `TreeSelect` model to `vizro-core/src/vizro/models/_components/form/` that wraps `fac.AntdTreeSelect` from `feffery-antd-components`. It is a hierarchical multi/single-select component for use as a `Parameter` selector only (not `Filter`).

## Model Fields

```python
class TreeSelect(VizroBaseModel):
    type: Literal["tree_select"] = "tree_select"
    options: TreeOptionsType                         # nested dict, see format below
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
    extra: SkipJsonSchema[dict[str, Any]] = {}
```

Note: `variant` is **not** included. AntdTreeSelect is a third-party component whose CSS cannot be targeted by the existing Vizro `dropdown-plain` class rule, so `variant` would be a no-op.

## options Type

`options` is typed as `dict[str, Any]` (required, no default). Structural validation is done in a `model_validator(mode="before")` that recursively checks: values are either a list of strings or a dict (recursing into dicts). Anything else raises a `ValueError` with a descriptive message. No recursive `TypeAlias` is used — Pydantic v2 does not support self-referential `TypeAlias`.

Example:

```python
{
    "Electronics": {
        "Phones": ["iPhone 15", "Android"],
        "Laptops": ["MacBook", "ThinkPad"],
    },
    "Clothing": ["Shirts", "Trousers"],
}
```

## Options Conversion

A private module-level `_convert_options(d)` helper recursively converts the nested dict to `AntdTreeSelect` `treeData` format:

- Dict values → `[{"title": k, "key": k, "value": k, "children": _convert_options(v)} for k, v in d.items()]`
- List values → `[{"title": v, "key": v, "value": v} for v in items]`

A second helper `_extract_leaf_keys(d) -> set[str]` recursively collects all leaf string values from the nested dict for use in value validation.

## value Handling

- Stored default is `None` for both `multi=True` and `multi=False`.
- At build time, if `value is None` and `multi=True`, defaults to `[]`; if `multi=False`, defaults to `None` (no selection — AntdTreeSelect renders with empty selection, which is acceptable for a Parameter selector).
- `_validate_tree_value`: mirrors `validate_value` in `_form_utils.py`. Guards with `if "options" not in info.data: return value` (dead code when `options` passes its own validator, but needed for safety when `options` itself fails validation). Calls `_extract_leaf_keys(info.data["options"])` and checks all values are in the leaf set.
- `_validate_multi`: same pattern as Dropdown — raises if `multi=False` and value is a list.

## __call__ Signature

Since TreeSelect is Parameter-only (no dynamic filter machinery), `__call__` takes no arguments and reads `self.options` directly:

```python
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
        "allowClear": self.multi,   # mirrors Dropdown's clearable=self.multi
        # showCheckedStrategy and maxTagCount only passed when multi=True to avoid passing None to AntdTreeSelect
        **( {"showCheckedStrategy": "show-child", "maxTagCount": "responsive"} if self.multi else {} ),
        "listHeight": 300,
        "locale": "en-us",
        "persistence": True,
        "persistence_type": "session",
        "placeholder": "Select option",
    }

    return html.Div([
        dbc.Label(
            [html.Span(id=f"{self.id}_title", children=self.title), *description],
            html_for=self.id,
        ) if self.title else None,
        fac.AntdTreeSelect(**(defaults | self.extra)),
    ])

@_log_call
def build(self):
    return self.__call__()
```

## Action Integration

Same pattern as Dropdown:

```python
@property
def _action_triggers(self): return {"__default__": f"{self.id}.value"}

@property
def _action_outputs(self):
    return {
        "__default__": f"{self.id}.value",
        **({"title": f"{self.id}_title.children"} if self.title else {}),
        **({"description": f"{self.description.id}-text.children"} if self.description else {}),
    }

@property
def _action_inputs(self): return {"__default__": f"{self.id}.value"}
```

## Dependencies

Add `feffery-antd-components` to `vizro-core/pyproject.toml` dependencies.

## Registration (all steps)

1. Create `vizro-core/src/vizro/models/_components/form/tree_select.py`
2. Export from `vizro-core/src/vizro/models/_components/form/__init__.py`
3. Export from `vizro-core/src/vizro/models/__init__.py` — add `TreeSelect` to `__all__`
4. Add `TreeOptionsType = dict[str, Any]` to `vizro-core/src/vizro/models/types.py` as a readable alias (structural validation is done in the model_validator, not the type annotation)
5. Add `TreeSelect` to the `SelectorType` forward-ref string in `types.py`:
   ```python
   "Checklist | DatePicker | Dropdown | RadioItems | RangeSlider | Slider | Switch | TreeSelect"
   ```
6. `TreeSelect.model_rebuild()` is called automatically via the `model_rebuild()` loop in `vizro/models/__init__.py` since it iterates `__all__`.

## Out of Scope

- Filter integration (no dataframe → options derivation)
- `_dynamic` / `_build_dynamic_placeholder`
- `_in_container` / inline layout
- `variant` field (no applicable CSS)
- `show_select_all` (AntdTreeSelect handles this natively via parent checkboxes)
- `_inner_component_properties` (not needed without dynamic filter machinery)
- tests
