# How to create custom actions

This guide demonstrates the usage of custom actions, an idea that shares similarities with, but is not identical to [callbacks](https://dash.plotly.com/basic-callbacks) in `Dash`.
If you want to use the [`Action`][vizro.models.Action] model to perform functions that are not available in the [pre-defined action functions][vizro.actions], you can create your own custom action.
Like other [actions](actions.md), custom actions could also be added as an element inside the [actions chain](actions.md#chain-actions), and it can be triggered with one of many dashboard components.

<!-- vale off -->
## Simple custom actions

Custom actions enable you to implement your own action function. Simply do the following:

1. define a function
2. decorate it with the `@capture("action")` decorator
3. add it as a `function` argument inside the [`Action`][vizro.models.Action] model

The following example shows how to create a custom action that postpones execution of the next action in the chain for `t` seconds.

!!! example "Simple custom action"
    === "app.py"
        ```py
        import vizro.models as vm
        import vizro.plotly.express as px
        from vizro import Vizro
        from vizro.actions import export_data
        from vizro.models.types import capture
        from time import sleep


        @capture("action")
        def my_custom_action(t: int):
            """Custom action."""
            sleep(t)


        df = px.data.iris()

        page = vm.Page(
            title="Example of a simple custom action",
            components=[
                vm.Graph(
                    figure=px.scatter(df, x="sepal_length", y="petal_width", color="species")
                ),
                vm.Button(
                    text="Export data",
                    actions=[
                        vm.Action(function=export_data()),
                        vm.Action(
                            function=my_custom_action(t=2)
                        ),
                        vm.Action(function=export_data(file_format="xlsx")),
                    ]
                )
            ],
            controls=[vm.Filter(column="species", selector=vm.Dropdown(title="Species"))],
        )

        dashboard = vm.Dashboard(pages=[page])

        Vizro().build(dashboard).run()
        ```
    === "app.yaml"
        ```yaml
        # Custom actions are currently only possible via python configuration
        ```
<!-- vale on -->


## Interact with dashboard inputs and outputs
When a custom action needs to interact with the dashboard, it is possible to define `inputs` and `outputs` for the custom action.

- `inputs` represents dashboard component properties whose values are passed to the custom action function as arguments. It is a list of strings in the format `"<component_id>.<property>"` (for example, `"scatter_chart.clickData`").
- `outputs` represents dashboard component properties corresponding to the custom action function return value(s). Similar to `inputs`, it is a list of strings in the format `"<component_id>.<property>"` (for example, `"my_card.children"`).

The following example shows how to create a custom action that shows the clicked chart data in a [`Card`][vizro.models.Card] component. For further information on the structure and content of the `clickData` property, refer to the Dash documentation on [interactive visualizations](https://dash.plotly.com/interactive-graphing).

!!! example "Custom action with dashboard inputs and outputs"

    === "app.py"
        ```py
        import vizro.models as vm
        import vizro.plotly.express as px
        from vizro import Vizro
        from vizro.actions import filter_interaction
        from vizro.models.types import capture


        @capture("action")
        def my_custom_action(show_species: bool, points_data: dict): # (1)!
            """Custom action."""
            clicked_point = points_data["points"][0]
            x, y = clicked_point["x"], clicked_point["y"]
            text = f"Clicked point has sepal length {x}, petal width {y}"

            if show_species:
                species = clicked_point["customdata"][0]
                text += f" and species {species}"
            return text


        df = px.data.iris()

        page = vm.Page(
            title="Example of a custom action with UI inputs and outputs",
            layout=vm.Layout(
                grid=[
                    [0, 2],
                    [0, 2],
                    [0, 2],
                    [1, -1],
                ],
                row_gap="25px",
            ),
            components=[
                vm.Graph(
                    id="scatter_chart",
                    figure=px.scatter(df, x="sepal_length", y="petal_width", color="species", custom_data=["species"]),
                    actions=[
                        vm.Action(function=filter_interaction(targets=["scatter_chart_2"])),
                        vm.Action(
                            function=my_custom_action(show_species=True), # (2)!
                            inputs=["scatter_chart.clickData"], # (3)!
                            outputs=["my_card.children"],
                        ),
                    ],
                ),
                vm.Card(id="my_card", text="Click on a point on the above graph."),
                vm.Graph(
                    id="scatter_chart_2",
                    figure=px.scatter(df, x="sepal_length", y="petal_width", color="species"),
                ),
            ],
            controls=[vm.Filter(column="species", selector=vm.Dropdown(title="Species"))],
        )

        dashboard = vm.Dashboard(pages=[page])

        Vizro().build(dashboard).run()
        ```

        1. Just as for any Python function, the names of the arguments `show_species` and `points_data` are arbitrary and do not need to match on to the names of `inputs` in any particular way.
        2. We _bind_ (set) the argument `show_species` to the value `True` in the initial specification of the `function` field. These are static values that are fixed when the dashboard is _built_.
        3. The content of `inputs` will "fill in the gaps" by setting values for the remaining unbound arguments in `my_custom_action`. Here there is one such argument, named `points_data`. Values for these are bound _dynamically at runtime_ to reflect the live state of your dashboard.
    === "app.yaml"
        ```yaml
        # Custom actions are currently only possible via python configuration
        ```
    === "Result"
        [![CustomAction]][CustomAction]

    [CustomAction]: ../../assets/user_guides/custom_actions/custom_action_inputs_outputs.png

## Multiple return values
The return value of the custom action function is propagated to the dashboard components that are defined in the `outputs` argument of the [`Action`][vizro.models.Action] model.
If there is a single `output` defined then the function return value is directly assigned to the component property.
If there are multiple `outputs` defined then the return value is iterated through and each part is assigned to each component property given in `outputs` in turn. This behavior is identical to Python's flexibility in managing multiple return values.

!!! example "Custom action with multiple return values"
    === "app.py"
        ```py
        import vizro.models as vm
        import vizro.plotly.express as px
        from vizro import Vizro
        from vizro.models.types import capture


        @capture("action")
        def my_custom_action(points_data: dict):
            """Custom action."""
            clicked_point = points_data["points"][0]
            x, y = clicked_point["x"], clicked_point["y"]
            species = clicked_point["customdata"][0]
            card_1_text = f"Clicked point has sepal length {x}, petal width {y}"
            card_2_text = f"Clicked point has species {species}"
            return card_1_text, card_2_text # (1)!


        df = px.data.iris()

        page = vm.Page(
            title="Example of a custom action with UI inputs and outputs",
            layout=vm.Layout(
                grid=[
                    [0, 0],
                    [0, 0],
                    [0, 0],
                    [1, 2],
                ],
                row_gap="25px",
            ),
            components=[
                vm.Graph(
                    id="scatter_chart",
                    figure=px.scatter(df, x="sepal_length", y="petal_width", color="species", custom_data=["species"]),
                    actions=[
                        vm.Action(
                            function=my_custom_action(),
                            inputs=["scatter_chart.clickData"],
                            outputs=["my_card_1.children", "my_card_2.children"], # (2)!
                        ),
                    ],
                ),
                vm.Card(id="my_card_1", text="Click on a point on the above graph."),
                vm.Card(id="my_card_2", text="Click on a point on the above graph."),
            ],
            controls=[vm.Filter(column="species", selector=vm.Dropdown(title="Species"))],
        )

        dashboard = vm.Dashboard(pages=[page])

        Vizro().build(dashboard).run()
        ```

        1. `my_custom_action` returns two values (which will be in Python tuple).
        2. These values are assigned to the `outputs` in the same order.
    === "app.yaml"
        ```yaml
        # Custom actions are currently only possible via python configuration
        ```
    === "Result"
        [![CustomAction2]][CustomAction2]

    [CustomAction2]: ../../assets/user_guides/custom_actions/custom_action_multiple_return_values.png


!!! warning

    Note that users of this package are responsible for the content of any custom action function that they write - especially with regard to leaking any sensitive information or exposing to any security threat during implementation. You should always [treat the content of user input as untrusted](https://community.plotly.com/t/writing-secure-dash-apps-community-thread/54619).
