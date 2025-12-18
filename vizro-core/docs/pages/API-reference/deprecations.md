# Deprecations and breaking changes

This page lists Vizro features that are now deprecated and forthcoming breaking changes for Vizro 0.2.0.

## `Layout` model

The [`Layout`][vizro.models.Layout] model has been renamed [`Grid`][vizro.models.Grid]. Replace your references to `Layout` with `Grid`.

```python
# Before:
vm.Layout(grid=[[0, 1], [2, 3]])

# After:
vm.Grid(grid=[[0, 1], [2, 3]])
```

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

Passing a static argument to a [custom action](../user-guides/custom-actions.md) is deprecated. All arguments must instead be [runtime inputs](../user-guides/custom-actions.md#trigger-with-a-runtime-input). For example, in Vizro 0.2.0, the following will no longer be possible:

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

## `filter_interaction`

`filter_interaction` is deprecated. Use the more powerful and flexible [`set_control`][vizro.actions.set_control].

```python
# Before:
components = [
    vm.AgGrid(..., actions=va.filter_interaction(targets=["target_chart"]),
    vm.Graph(id="target_chart", ...)
]

# After:
components = [
    vm.AgGrid(..., actions=va.set_control(control="my_filter", value="species")),
    vm.Graph(id="target_chart", ...)
]
# You must now explicitly specify a Filter in controls:
controls = [vm.Filter(id="my_filter", targets=["target_chart"], column="species")]
```

See the [user guide on how to interact with graphs and tables](../user-guides/graph-table-actions.md) for more information.
