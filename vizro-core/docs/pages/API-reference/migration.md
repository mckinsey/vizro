---
description: "Migration guide for Vizro 1.0.0: how to update code that used APIs removed or changed in the 1.0.0 breaking release (`Layout`→`Grid`, `RangeSlider`→`Slider(range=True)`, `AgGrid`/Dash DataTable→`Table` with `dash_ag_grid`, `set_control`/`filter_interaction`→`set_controls`, `Action.inputs`, and the `Cascader.full_path` default)."
---

# Migration guide

This page documents the APIs removed or changed in the Vizro 1.0.0 breaking release and how to migrate your code. Each section shows the before/after.

## `Layout` model

The `Layout` model has been renamed [`Grid`][vizro.models.Grid]. Replace your references to `Layout` with `Grid`.

```python
# Before:
vm.Layout(grid=[[0, 1], [2, 3]])

# After:
vm.Grid(grid=[[0, 1], [2, 3]])
```

## `RangeSlider` model

The `RangeSlider` model has been removed. Use [`Slider`][vizro.models.Slider] with `range=True`, which is functionally identical.

```python
# Before:
vm.RangeSlider(min=0, max=10)

# After:
vm.Slider(min=0, max=10, range=True)
```

In YAML or JSON configuration, replace `type: range_slider` with `type: slider` and add `range: true`.

See the [user guide on selectors](../user-guides/selectors.md#numerical-selectors) for more information.

## `filter_interaction`

`filter_interaction` is deprecated. Use the more powerful and flexible [`set_controls`][vizro.actions.set_controls].

```python
# Before:
components = [
    vm.Table(..., actions=va.filter_interaction(targets=["target_chart"])),
    vm.Graph(id="target_chart", ...)
]

# After:
components = [
    vm.Table(..., actions=va.set_controls(controls=["my_filter"], value="species")),
    vm.Graph(id="target_chart", ...)
]
# You must now explicitly specify a Filter in controls:
controls = [vm.Filter(id="my_filter", targets=["target_chart"], column="species")]
```

See the [user guide on how to interact with graphs and tables](../user-guides/graph-table-actions.md) for more information.

## `set_control` action

The `set_control` action has been removed. Use [`set_controls`][vizro.actions.set_controls], which takes one or more control ids via `controls` (a single id or a list) and is otherwise identical.

```python
# Before:
va.set_control(control="my_filter", value="species")
va.set_control(control=["filter_1", "filter_2"], value="species")

# After:
va.set_controls(controls="my_filter", value="species")  # a single id
va.set_controls(controls=["filter_1", "filter_2"], value="species")  # or a list of ids
```

See the [user guide on how to interact with graphs and tables](../user-guides/graph-table-actions.md) for more information.

## `Action` model `inputs` argument

The `inputs` argument of the [`Action` model][vizro.models.Action] is deprecated. Pass references to runtime inputs directly as arguments of `function`.

```python
# Before:
vm.Action(function=my_action(), inputs=["dropdown.value"], outputs=["text.children"])

# After:
vm.Action(function=my_action("dropdown.value"), outputs=["text.children"])
# In fact, just this would work and is preferred:
vm.Action(function=my_action("dropdown"), outputs="text")
```

See the [user guide on custom actions](../user-guides/custom-actions.md#trigger-with-a-runtime-input) for more information.

## Static argument for custom action

Passing a static argument to a [custom action](../user-guides/custom-actions.md) is deprecated. All arguments must instead be [runtime inputs](../user-guides/custom-actions.md#trigger-with-a-runtime-input). For example, in Vizro 1.0.0, the following will no longer be possible:

```python
@capture("action")
def my_action(static_argument):
    ...

vm.Action(function=my_action(static_argument=1), ...)
```

Does this cause you a problem? Please [let us know](https://github.com/mckinsey/vizro/issues)!

## `Action` model for built-in action

Using the [`Action` model][vizro.models.Action] for built-in actions is deprecated.
Call the action directly:

```python
# Before:
vm.Action(function=va.export_data(file_format="xlsx"))

# After:
va.export_data(file_format="xlsx")
```

See the [user guide on built-in actions](../user-guides/actions.md) for more information.

## Action `type` required in dict / YAML / JSON

When an action is configured as a dictionary (or in YAML/JSON), it must now declare an explicit `type`, like every other model. Previously a custom action could omit `type` and was assumed to be an `Action`; that fallback has been removed.

```yaml
# Before (type omitted, implicitly treated as a custom action):
actions:
  - function:
      _target_: my_custom_function

# After:
actions:
  - type: action
    function:
      _target_: my_custom_function
```

Built-in actions already required their `type` (for example `type: export_data`), so they are unaffected, and Python configuration is unaffected because each action object already carries its `type`.

## `Cascader` `full_path` default

The default of [`Cascader`][vizro.models.Cascader]'s `full_path` argument will change from `False` to `True` in Vizro 1.0.0. To keep the current behavior, set `full_path=False` explicitly.

```python
# Before (relies on the default, which will change in Vizro 1.0.0):
vm.Cascader(options=...)

# After (keeps the current behavior):
vm.Cascader(options=..., full_path=False)
```

See the [user guide on selectors](../user-guides/selectors.md#hierarchical-selectors) for more information.

## `AgGrid` model

The `AgGrid` model has been removed. Use [`Table`][vizro.models.Table] with a `dash_ag_grid` figure, which is functionally identical.

```python
# Before:
vm.AgGrid(figure=dash_ag_grid(data_frame=df))

# After:
vm.Table(figure=dash_ag_grid(data_frame=df))
```

In YAML or JSON configuration, replace `type: ag_grid` with `type: table` (keeping the `dash_ag_grid` figure).

See the [user guide on how to use tables](../user-guides/table.md) for more information.

## Dash DataTable backing

Backing a [`Table`][vizro.models.Table] with a Dash `DataTable` (via `dash_data_table`) is deprecated. From Vizro 1.0.0, `Table` supports only a `dash_ag_grid` figure, which renders an interactive AG Grid.

```python
# Before:
vm.Table(figure=dash_data_table(data_frame=df))

# After:
vm.Table(figure=dash_ag_grid(data_frame=df))
```

See the [user guide on how to use tables](../user-guides/table.md) for more information.
