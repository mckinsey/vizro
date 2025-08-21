# How to create custom actions

Actions dictate how your app behaves in response to user input, for example what happens when someone clicks a button or a point on a graph. If you need to perform a function that are not available in Vizro's [built-in actions](actions.md) then you need to write your own custom action. We also have an in-depth [tutorial on writing your own action](../tutorials/custom-actions.md) that teaches many of the concepts you see here in more detail.

Vizro's actions system is built on top of [Dash callbacks](https://dash.plotly.com/basic-callbacks), but you do not need to know anything about Dash callbacks to use them. If you are already familiar with Dash callbacks then you might like to also read our [explanation of how Vizro actions compare to Dash callbacks](../explanation/actions-and-callbacks.md).

!!! note

    Do you have an idea for a built-in action that you think would be useful for many Vizro users? Let us know by submitting a [feature request](https://github.com/mckinsey/vizro/issues/new?template=feature-request.yml)!

## General principles

Many [Vizro models][vizro.models] have an `actions` argument that can contain one or more actions. Each action is a Python function that is _triggered_ when a user interacts with a component on their screen. This function can depend on _inputs_ and update _outputs_.

To define your own action:

1. write a Python function
1. decorate it with `@capture("action")`
1. attach it to the `actions` argument of a Vizro model using [`Action`][vizro.models.Action]:
    1. call it using the `function` argument
    1. if your action has one or more inputs then specify them as function arguments
    1. if your action has one or more outputs then specify them as `outputs`

Generally speaking, an action's `outputs` and input function arguments are strings that refer to Vizro model `id`s. For example, to write an action that updates the Plotly figure inside [a Graph component](graph.md) `vm.Graph(id="my_graph", header="Graph header")`, you would use `outputs="my_graph"`. It is also possible to [use specific model arguments](#model-arguments-as-input-and-output) or even [Dash properties](#dash-properties-as-input-and-output) as action inputs and outputs, for example with `outputs="my_graph.header"`.

Here's an example of the syntax for an action with two inputs and one output:

```python
from vizro.models.types import capture


@capture("action")
def action_function(input_1, input_2):
    ...
    return "value 1"  # (1)!
```

1. An action can return values of any Python type that can be converted to JSON. It is also valid to have an action that has no return values, in which case `outputs` should not be specified.

This would then be used in a Vizro model's `actions` argument as follows:

```python
import vizro.models as vm

actions = vm.Action(
    function=action_function("input_id_1", "input_id_2"),  # (1)!
    outputs="output_id_1",  # (2)!
)
```

1. Here we used positional arguments but, just like a normal Python function call, you could also use keyword arguments as `action_function(input_1="input_id_1", input_2="input_id_2")`.

### Actions chain

<!-- TODO NOW: link this to actions chain correctly -->

If you define multiple actions in an actions chain then you can freely mix built-in and custom actions. Built-in actions and custom actions behave identically in terms of when they are triggered.

Here is an example chain including the custom actions `action_function` and `another_action_function` and the built-in `export_data`:

```python
actions = [
    vm.Action(
        function=action_function("input_id_1", "input_id_2"),
        outputs="output_id_1",
    ),
    vm.Action(
        function=action_function("input_id_1", "input_id_3"),  # (1)!
        outputs="output_id_2",
    ),
    vm.Action(
        function=another_action_function(),  # (2)!
        outputs=["output_id_1", "output_id_2"],  # (3)!
    ),
    export_data(),  # (4)!
]
```

1. You can use the same action function multiple times throughout your app, even in the same actions chain. The same input `input_id_1` can also be used multiple times.
1. This action has no inputs and two outputs. `another_action_function` would need to return multiple values, such as `return "value_1", "value_2"`.
1. The same output can be used multiple times throughout your app, even in the same actions chain.
1. This is an example of a built-in action, available as `from vizro.actions import export_data`. It does not use the `vm.Action` model.

!!! tip "Multiple return values"

    The returned values of an action function with multiple outputs are matched to the `outputs` in order. For actions with many return values, it can be a good idea to instead return a dictionary where returned values are labelled by string keys. In this case, `outputs` should also be a dictionary with matching keys, and the order of entries does not matter.

### Security

When writing actions, uou should never assume that the value of inputs in your action function is restricted to those that show on the user's screen. A malicious user can execute your action functions with arbitrary inputs. In the tutorial, we discuss in more detail [how to write secure actions](../tutorials/custom-actions.md#security).

## Trigger an action with a button

It is very common to use a [button](button.md) to trigger an action. Here is an example based on our [companion tutorial on custom actions](../tutorials/custom-actions.md). We have an action `update_text` finds the current time using a 12- or 24-hour clock.

```python
from datetime import datetime
from vizro.models.types import capture


@capture("action")
def update_text(use_24_hour_clock):  # (1)!
    time_format = "%H:%M:%S %Z" if use_24_hour_clock else "%I:%M:%S %p %Z"
    time = datetime.now().strftime(time_format)
    return f"The time is {time}"  # (2)!
```

1. The function has one argument, which will receive a boolean value `True` or `False` to determine the time format used.
1. The function returns a single value.

To attach the action to a button model, we use it inside the `actions` argument as follows:

```python
(
    vm.Button(
        actions=vm.Action(
            function=update_text(use_24_hour_clock="clock_switch"),  # (1)!
            outputs="time_text",  # (2)!
        ),
    ),
)
```

1. The argument `use_24_hour_clock` corresponds to the value of the component with `id="clock_switch"` (not yet defined).
1. The returned value "The time is ..." will update the component `id="time_text"` (not yet defined).

Here is the full example code that includes the input component `vm.Switch(id="clock_switch")` and output component `vm.Time(id="time_text")`.

!!! example "Trigger an action with a button"

    === "app.py"

        ```{.python hl_lines="8-12 22-27"}
        from datetime import datetime

        import vizro.models as vm
        from vizro import Vizro
        from vizro.models.types import capture


        @capture("action")
        def update_text(use_24_hour_clock):
            time_format = "%H:%M:%S %Z" if use_24_hour_clock else "%I:%M:%S %p %Z"
            time = datetime.now().strftime(time_format)
            return f"The time is {time}"


        vm.Page.add_type("components", vm.Switch)  # (1)!

        page = vm.Page(
            title="Action trigger by button",
            layout=vm.Flex(),
            components=[
                vm.Switch(id="clock_switch", title="24-hour clock", value=True),
                vm.Button(
                    actions=vm.Action(
                        function=update_text(use_24_hour_clock="clock_switch"),
                        outputs="time_text",
                    ),
                ),
                vm.Text(id="time_text", text="Click the button"),
            ],
        )

        dashboard = vm.Dashboard(pages=[page])
        Vizro().build(dashboard).run()

        ```

        1. Currently [`Switch`][vizro.models.Switch] is designed to be used as a [control selectors](../user-guides/selectors.md). In future, Vizro will have a dedicated `Form` model for the creation of forms. For now, we add them directly as `components` inside a [`Container`][vizro.models.Container]. For this to be a valid configuration we must first do `add_type` as for a [custom component](../user-guides/custom-components.md).

    === "Result"

        TODO screenshot

Before clicking the button, the text shows "Click the button". When you click the button, the `update_text` action is triggered. This finds the current time and returns a string "The time is ...". The resulting value is sent back to the user's screen and updates the text of the model `vm.Text(id="time_text")`.

For more advanced variants based on this, such as multiple inputs and outputs and actions chains, refer to the [full tutorial](../tutorials/custom-actions.md).

!!! tip

    If you have many buttons that trigger actions then you might like to [give them icons](button.md/#add-an-icon). You can even have icon-only buttons with no text.

## Trigger an action with a graph

This is already possible, and documentation is coming soon!

## Address specific parts of a model

For most actions that you write, you should only need to specify `<model_id>` for the `outputs` or as input arguments to the action function. However, some models have multiple arguments that you may want to use in an action, in which case you should use the syntax [`<model_id>.<argument_name>`](#model-arguments-as-input-and-output). For more advanced use cases you may even need to [address the underlying Dash component and property](#dash-properties-as-input-and-output).

### Model arguments as input and output

The syntax for using a particular model argument as an action input or output is `<model_id>.<argument_name>`. For example, let's alter the [above example](#trigger-an-action-with-a-button) that specifies the 12- or 24-hour clock. In the previous code, the action was triggered when a button is clicked; now we change the action to be triggered when the switch itself is clicked. We also now want to update the `title` of the switch at the same time. We do this by using `"clock_switch.title"` in `outputs`. We highlight the code changes below.

!!! example "Use model argument as output"

    === "app.py"

        ```{.python hl_lines="11 13 26-29"}
        from datetime import datetime

        import vizro.models as vm
        from vizro import Vizro
        from vizro.models.types import capture


        @capture("action")
        def update_text(use_24_hour_clock):
            time_format = "%H:%M:%S %Z" if use_24_hour_clock else "%I:%M:%S %p %Z"
            switch_title = "24-hour clock" if use_24_hour_clock else "12-hour clock"
            time = datetime.now().strftime(time_format)
            return f"The time is {time}", switch_title


        vm.Page.add_type("components", vm.Switch)  # (1)!

        page = vm.Page(
            title="Action triggered by switch",
            layout=vm.Flex(),
            components=[
                vm.Switch(
                    id="clock_switch",
                    title="24-hour clock",
                    value=True,
                    actions=vm.Action(
                        function=update_text(use_24_hour_clock="clock_switch"),
                        outputs=["time_text", "clock_switch.title"],  # (2)!
                    ),
                ),
                vm.Text(id="time_text", text="Toggle the switch"),
            ],
        )

        dashboard = vm.Dashboard(pages=[page])
        Vizro().build(dashboard).run()
        ```

        1. Currently [`Switch`][vizro.models.Switch] is designed to be used as a [control selectors](../user-guides/selectors.md). In future, Vizro will have a dedicated `Form` model for the creation of forms. For now, we add them directly as `components` inside a [`Container`][vizro.models.Container]. For this to be a valid configuration we must first do `add_type` as for a [custom component](../user-guides/custom-components.md).
        1. This action now has two `outputs`. We refer to `"clock_switch.title"` to update the title of the switch.

    === "Result"

        TODO screenshot

In fact, whenever we refer to just a model `id` as an action's input or output, it is just shorthand for the full `<model_id>.<argument_name>`, with some appropriate default argument name chosen for the model. This default corresponds to the most common argument that you would use for an action's input and output. In the above example, the input `use_24_hour_clock="clock_switch"` is equivalent to writing `use_24_hour_clock="clock_switch.value"`, and the output `"time_text"` is equivalent to writing `"time_text.text"`. If you prefer to be explicit then you can write these full versions and the app will work exactly the same way.

Some arguments, or even whole models, are available for use as an action input but not output or vice versa. For example, `vm.Text` is available as an action output but not input.

!!! note

    If you would like to use as an input or output something that is not available then you may be able to achieve it by [explicitly addressing the underlying Dash component property](#dash-properties-as-input-and-output). If you think there should be a direct way to address the component in Vizro then let us know by submitting a [feature request](https://github.com/mckinsey/vizro/issues/new?template=feature-request.yml)!

### Dash properties as input and output

Sometimes you might like to use as input or output a component that is on the screen but cannot be addressed explicitly with `<model_id>.<argument_name>`. Vizro actions in fact accept as input and output _any_ Dash component in the format `<component_id>.<property>`.

Most Vizro models produce multiple Dash components, each of which has several properties. The above examples' `vm.Switch(id="clock_switch", title="24-hour clock", value=True)` produces something like the following:

```py
import dash_bootstrap_components as dbc
from dash import html

dbc.Switch(
    id="clock_switch",
    value=True,
    label=html.Span(id="clock_switch_title", children="24-hour-clock"),
)
```

As well as the "core" [`dbc.Switch` component](https://www.dash-bootstrap-components.com/docs/components/input/), the `vm.Switch` model produces a [`html.Span` component](https://dash.plotly.com/dash-html-components/span) to contain the value of the `title` argument. Sometimes there may be Dash components that you wish to use as an action input or output that are not easily mapped onto Vizro model arguments. In this case, you should [consult the model's source code](https://github.com/mckinsey/vizro/tree/main/vizro-core/src/vizro/models) to find the relevant Dash component and property. The `id` of Dash components are always prefixed by the model `id`. For example, `vm.Graph(id="my_graph")` would produce Dash components with `id="my_graph_title"`, `id="my_graph_header"`, `id="my_graph_footer"`, and so on.

In fact, Vizro's system of `<model_id>.<argument_name>` is just shorthand for the underlying Dash `<component_id>.<property>`. For example, `"clock_switch.title"` is equivalent to `"clock_switch_title.children"`. Wherever possible, you should prefer to use the Vizro shorthands rather than referring to the underlying Dash components (for example, use `"clock_switch.title"` in preference to `"clock_switch_title.children"`). This is more intuitive and more stable. While using a pure Dash component `id` and property will indefinitely remain possible in Vizro actions, we consider the exact underlying Dash components to be implementation details, and so the Dash components available and their `id`s may change between non-breaking Vizro releases.

!!! note

    Are you addressing an underlying Dash component that you think should be addressed by Vizro more easily? Let us know by submitting a [feature request](https://github.com/mckinsey/vizro/issues/new?template=feature-request.yml)!

### Recap

To summarise the above sections on addressing specific parts of a model, we have seen the following equivalences:

- `"clock_switch"` is shorthand for `"clock_switch.value"`. In this case, the Vizro `<model_id>.<argument_name>` is the same as the underlying Dash `<component_name>.<property>`.
- `"time_text"` is shorthand for `"time_text.text"`, which itself refers to the underlying Dash property`"time_text.children"`.
- `"clock_switch.title"` is shorthand for (and should be used in preference to) the underlying Dash property `"clock_switch_title.children"`.

If you are already familiar with Dash then here are some other common equivalences that are useful to know:

- `"my_button"` is shorthand for the underlying Dash property `"my_button.n_clicks"`.
- `"my_graph` is shorthand for the underlying Dash property `"my_graph.figure"`.
- For all [selectors](selectors.md), `"my_selector"` is shorthand for the underlying Dash property `"my_selector.value"`.

<!--
TODO NOW:
- YAML configuration
- Remove old screenshots
-->
