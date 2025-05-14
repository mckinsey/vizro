# How to create custom actions

This guide demonstrates the usage of custom actions, an idea that shares similarities with, but is not identical to [callbacks](https://dash.plotly.com/basic-callbacks) in `Dash`. If you want to use the [`Action`][vizro.models.Action] model to perform functions that are not available in the [built-in action functions][vizro.actions], you can create your own custom action. Like other [actions](actions.md), custom actions could also be added as an element inside the [actions chain](actions.md#chain-actions), and it can be triggered with one of many dashboard components.

<!-- vale off -->

## Simple custom action

Custom actions enable you to implement your own action function. Simply do the following:

1. define a function
1. decorate it with the `@capture("action")` decorator
1. add it as a `function` argument inside the [`Action`][vizro.models.Action] model

The following example shows how to create a custom action that postpones execution of the next action in the chain for `t` seconds.

!!! example "Simple custom action"

    === "app.py"

        ```{.python pycafe-link extra-requirements="openpyxl"}
        import vizro.models as vm
        import vizro.plotly.express as px
        from vizro import Vizro
        from vizro.actions import export_data
        from vizro.models.types import capture
        from time import sleep


        @capture("action")  # (1)!
        def my_custom_action(t: int):
            sleep(t)


        df = px.data.iris()

        page = vm.Page(
            title="Simple custom action",
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
            ]
        )

        dashboard = vm.Dashboard(pages=[page])
        Vizro().build(dashboard).run()
        ```

        1. We define a custom action `my_custom_action` using the `@capture("action")` decorator. This action takes an integer `t` and pauses execution for `t` seconds. It's used here to delay the subsequent `export_data` action in the chain.

    === "app.yaml"

        Custom actions are currently only possible via Python configuration.

<!-- vale on -->

## Interact with inputs and outputs

When a custom action needs to interact with the dashboard, it is possible to define `inputs` and `outputs` for the custom action.

- `inputs` represents dashboard component properties whose values are passed to the custom action function as arguments. It is a list of strings in the format `"<component_id>.<property>"` (for example, `"my_selector.value`").
- `outputs` represents dashboard component properties corresponding to the custom action function return value(s). Similar to `inputs`, it is a list of strings in the format `"<component_id>.<property>"` (for example, `"my_card.children"`).

### Example of `value` as input

The following example shows a custom action that takes the `value` of the `vm.RadioItem` and returns it inside a [`Card`][vizro.models.Card] component.

!!! example "Display `value` in Card"

    === "app.py"

        ```{.python pycafe-link}
        import vizro.models as vm
        import vizro.plotly.express as px
        from vizro import Vizro
        from vizro.models.types import capture

        df = px.data.iris()
        vm.Page.add_type("components", vm.RadioItems)

        @capture("action")  # (1)!
        def update_card_text(species):
            return f"You selected species **{species}**"

        page = vm.Page(
            title="Action with value as input",
            layout=vm.Grid(grid=[[0, 1]]),
            components=[
                vm.RadioItems(
                    id="my_selector",
                    title="Select a species:",
                    options=df["species"].unique().tolist(),
                    actions=[
                        vm.Action(function=update_card_text(), inputs=["my_selector.value"], outputs=["my_card.children"])
                    ],
                ),
                vm.Card(text="Placeholder text", id="my_card"),
            ],
        )

        dashboard = vm.Dashboard(pages=[page])
        Vizro().build(dashboard).run()
        ```

        1. We define a custom action `update_card_text` using the `@capture("action")` decorator. This action takes the selected `species` as input and returns a formatted string to be displayed in a Card.

    === "app.yaml"

        Custom actions are currently only possible via Python configuration.

    === "Result"

        [![ValueAction]][valueaction]

### Example of `clickData` as input

The following example shows how to create a custom action that shows the `clickData` of a chart in a [`Card`][vizro.models.Card] component. For further information on the structure and content of the `clickData` property, refer to the Dash documentation on [interactive visualizations](https://dash.plotly.com/interactive-graphing).

!!! example "Display `clickData` in Card"

    === "app.py"

        ```{.python pycafe-link}
        import vizro.models as vm
        import vizro.plotly.express as px
        from vizro import Vizro
        from vizro.models.types import capture

        df = px.data.iris()

        @capture("action")  # (1)!
        def my_custom_action(show_species: bool, points_data: dict):  # (2)!
            clicked_point = points_data["points"][0]
            x, y = clicked_point["x"], clicked_point["y"]
            text = f"Clicked point has sepal length {x}, petal width {y}"

            if show_species:
                species = clicked_point["customdata"][0]
                text += f" and species {species}"
            return text

        page = vm.Page(
            title="Action with clickData as input",
            components=[
                vm.Graph(
                    id="scatter_chart",
                    figure=px.scatter(df, x="sepal_length", y="petal_width", color="species", custom_data=["species"]),
                    actions=[
                        vm.Action(
                            function=my_custom_action(show_species=True), # (3)!
                            inputs=["scatter_chart.clickData"], # (4)!
                            outputs=["my_card.children"],
                        ),
                    ],
                ),
                vm.Card(id="my_card", text="Click on a point on the above graph."),
            ],
        )

        dashboard = vm.Dashboard(pages=[page])
        Vizro().build(dashboard).run()
        ```

        1. We define a custom action `my_custom_action` using the `@capture("action")` decorator.
        1. This action takes a boolean `show_species` and a dictionary `points_data`. It uses these to construct a descriptive string about a clicked point on a chart. The names `show_species` and `points_data` are arbitrary and do not need to match on to the names of `inputs` in any particular way.
        1. When the `Action` is defined within the `Graph.actions`, the `show_species` argument of `my_custom_action` is statically bound to `True`.
        1. The `points_data` argument of `my_custom_action` receives its value dynamically at runtime. This happens because the `inputs` parameter of `vm.Action` is set to `["scatter_chart.clickData"]`. When a user clicks on the `scatter_chart`, the chart's `clickData` property (which contains details about the click event) is automatically passed as the `points_data` argument to `my_custom_action`.

    === "app.yaml"

        Custom actions are currently only possible via Python configuration.

    === "Result"

        [![CustomAction]][customaction]

## Multiple return values

The return value of the custom action function is propagated to the dashboard components that are defined in the `outputs` argument of the [`Action`][vizro.models.Action] model. If there is a single `output` defined then the function return value is directly assigned to the component property. If there are multiple `outputs` defined then the return value is iterated through and each part is assigned to each component property given in `outputs` in turn. This behavior is identical to Python's flexibility in managing multiple return values.

!!! example "Multiple return values"

    === "app.py"

        ```{.python pycafe-link}
        import vizro.models as vm
        import vizro.plotly.express as px
        from vizro import Vizro
        from vizro.models.types import capture


        @capture("action")  # (1)!
        def my_custom_action(points_data: dict):
            clicked_point = points_data["points"][0]
            x, y = clicked_point["x"], clicked_point["y"]
            species = clicked_point["customdata"][0]
            card_1_text = f"Clicked point has sepal length {x}, petal width {y}"
            card_2_text = f"Clicked point has species {species}"
            return card_1_text, card_2_text


        df = px.data.iris()

        page = vm.Page(
            title="Example of a custom action with UI inputs and outputs",
            layout=vm.Flex(),  # (2)!
            components=[
                vm.Graph(
                    id="scatter_chart",
                    figure=px.scatter(df, x="sepal_length", y="petal_width", color="species", custom_data=["species"]),
                    actions=[
                        vm.Action(
                            function=my_custom_action(),
                            inputs=["scatter_chart.clickData"],
                            outputs=["my_card_1.children", "my_card_2.children"], # (3)!
                        ),
                    ],
                ),
                vm.Card(id="my_card_1", text="Click on a point on the above graph."),
                vm.Card(id="my_card_2", text="Click on a point on the above graph."),
            ]
        )

        dashboard = vm.Dashboard(pages=[page])
        Vizro().build(dashboard).run()
        ```

        1. We define a custom action `my_custom_action` using the `@capture("action")` decorator. This action takes `points_data` (dynamically populated from `scatter_chart.clickData`) as input, extracts details about the clicked point, and returns two strings, `card_1_text` and `card_2_text`.
        1. A [`Flex`][vizro.models.Flex] layout is used for the page to ensure the `Graph` and `Card` components are sized appropriately based on their content rather than being distributed evenly.
        1. The two strings returned by `my_custom_action` are assigned in the same order here.

    === "app.yaml"

        Custom actions are currently only possible via Python configuration.

    === "Result"

        [![CustomAction2]][customaction2]

!!! warning

    Note that users of this package are responsible for the content of any custom action function that they write. Take care to avoid leaking any sensitive information or exposing to any security threat during implementation. You should always [treat the content of user input as untrusted](https://community.plotly.com/t/writing-secure-dash-apps-community-thread/54619).

[customaction]: ../../assets/user_guides/custom_actions/clickdata_as_input.png
[customaction2]: ../../assets/user_guides/custom_actions/custom_action_multiple_return_values.png
[valueaction]: ../../assets/user_guides/custom_actions/value_as_input.png
