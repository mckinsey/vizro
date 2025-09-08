# Deprecations and breaking changes

This page lists Vizro features that are now deprecated and forthcoming breaking changes for Vizro 0.2.0.

## `Layout` model

The [`Layout`][vizro.models.Layout] model has been renamed [`Grid`][vizro.models.Grid], and `Layout` will not exist in Vizro 0.2.0. Replace your references to `Layout` with `Grid`.

```python
# Before:
vm.Layout(grid=[[0, 1], [2, 3]])
# After:
vm.Grid(grid=[[0, 1], [2, 3]])
```

## `Action` model `inputs` argument

The `inputs` argument has been deprecated and will not exist in Vizro 0.2.0. Pass references to runtime inputs directly as arguments of `function`:

```python
# Before:
vm.Action(function=my_action(), inputs=["dropdown.value"], outputs=["text.children"])
# After:
vm.Action(function=my_action("dropdown.value"), outputs=["text.children"])
# In fact, just this would work and is preferred:
vm.Action(function=action_function("dropdown"), outputs="text")
```

See the [user guide on custom actions](../user-guides/custom-actions.md#trigger-with-a-runtime-input) for more guidance.

## Static argument for custom action

Passing a static argument to a [custom action](../user-guides/custom-actions.md) has been deprecated and will not be possible in Vizro 0.2.0. All arguments must instead be [runtime inputs](../user-guides/custom-actions.md#trigger-with-a-runtime-input). For example, the following will no longer be possible:

```python
@capture("action")
def my_action(static_argument):
    ...

vm.Action(function=my_action(static_argument=1), ...)
```

Does this cause you a problem? Please [let us know](https://github.com/mckinsey/vizro/issues)!
