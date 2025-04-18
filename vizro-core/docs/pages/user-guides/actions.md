# How to use actions

This guide shows you how to use actions, an idea that is similar to [callbacks](https://dash.plotly.com/basic-callbacks) in `Dash`. Many components of a dashboard (for example, [`Graph`][vizro.models.Graph] or [`Button`][vizro.models.Button]) have an optional `actions` argument, where you can enter the [`Action`][vizro.models.Action] model.

By combining the [`Action`][vizro.models.Action] model with an action function, you can create complex dashboard interactions triggered by various events.

There are already a few action functions you can reuse:

- [`export_data`][vizro.actions.export_data]
- [`filter_interaction`][vizro.actions.filter_interaction]

## Built-in actions

To attach an action to a component, you must enter the [`Action`][vizro.models.Action] model into the component's `action` argument. You can then add a desired action function into the `function` argument of the [`Action`][vizro.models.Action].

??? note "Note on `Trigger`"

    Currently each component has one pre-defined trigger property. A trigger property is an attribute of the component that triggers a configured action (for example, for the `Button` it is `n_click`).

The below sections are guides on how to use action functions.

### Export data

To enable downloading data, you can add the [`export_data`][vizro.actions.export_data] action function to the [`Button`][vizro.models.Button] component. Hence, as a result, when a dashboard user now clicks the button, all data on the page will be downloaded.

!!! example "`export_data`"

    === "app.py"

        ```{.python pycafe-link}
        import vizro.models as vm
        import vizro.plotly.express as px
        from vizro import Vizro
        from vizro.actions import export_data

        df = px.data.iris()

        page = vm.Page(
            title="My first page",
            layout=vm.Flex(),  # (1)!
            components=[
                vm.Graph(
                    figure=px.scatter(
                        df,
                        x="sepal_width",
                        y="sepal_length",
                        color="species",
                        size="petal_length",
                    ),
                ),
                vm.Button(
                    text="Export data",
                    actions=[vm.Action(function=export_data())],
                ),
            ]
        )

        dashboard = vm.Dashboard(pages=[page])
        Vizro().build(dashboard).run()
        ```

        1. We use a [`Flex`][vizro.models.Flex] layout to make sure the `Graph` and `Button` only occupy as much space as they need, rather than being distributed evenly.

    === "app.yaml"

        ```yaml
        # Still requires a .py to add data to the data manager and parse YAML configuration
        # See yaml_version example
        pages:
          - components:
              - figure:
                  _target_: scatter
                  x: sepal_width
                  y: sepal_length
                  color: species
                  size: petal_length
                  data_frame: iris
                type: graph
              - type: button
                text: Export data
                id: export_data
                actions:
                  - function:
                      _target_: export_data
            layout:
              type: flex
            title: My first page
        ```

    === "Result"

        [![ExportData]][exportdata]

!!! note

    Note that exported data only reflects the original dataset and any native data modifications defined with [`vm.Filter`](filters.md), [`vm.Parameter`](data.md/#parametrize-data-loading) or [`filter_interaction`](actions.md/#cross-filtering) action. Filters from the chart itself, such as ag-grid filters, are not included, and neither are other chart modifications, nor any data transformations in custom charts.

### Cross-filtering

Cross-filtering enables you to click on data in one chart or table to filter other components in the dashboard. This is enabled using the [`filter_interaction`][vizro.actions.filter_interaction] action. It can be applied to [`Graph`][vizro.models.Graph], [`Table`][vizro.models.Table], and [`AgGrid`][vizro.models.AgGrid], and is currently triggered by click.

To configure cross-filtering using `filter_interaction`, follow these steps:

1. Add the action function to the source [`Graph`][vizro.models.Graph], [`Table`][vizro.models.Table] or [`AgGrid`][vizro.models.AgGrid] component and a list of IDs of the target charts into `targets`.

```py
actions=[vm.Action(function=filter_interaction(targets=["scatter_relation_2007"]))]
```

1. If the source chart is [`Graph`][vizro.models.Graph], enter the filter columns in the `custom_data` argument of the underlying source chart `function`.

```py
Graph(figure=px.scatter(..., custom_data=["continent"]))
```

Selecting a data point with a corresponding value of "Africa" in the continent column will result in filtering the data of target charts to show only entries with "Africa" in the continent column. The same applies when providing multiple columns in `custom_data`.

!!! note

    - You can reset your chart interaction filters by refreshing the page
    - You can create a "self-interaction" by providing the source chart id as its own `target`

Here is an example of how to configure a chart interaction when the source is a [`Graph`][vizro.models.Graph] component.

!!! example "Graph `filter_interaction`"

    === "app.py"

        ```{.python pycafe-link}
        import vizro.models as vm
        import vizro.plotly.express as px
        from vizro import Vizro
        from vizro.actions import filter_interaction

        df_gapminder = px.data.gapminder().query("year == 2007")
        page = vm.Page(
            title="Filter interaction",
            components=[
                vm.Graph(
                    figure=px.box(
                        df_gapminder,
                        x="continent",
                        y="lifeExp",
                        color="continent",
                        custom_data=["continent"],
                    ),
                    actions=[vm.Action(function=filter_interaction(targets=["scatter_relation_2007"]))],
                ),
                vm.Graph(
                    id="scatter_relation_2007",
                    figure=px.scatter(
                        df_gapminder,
                        x="gdpPercap",
                        y="lifeExp",
                        size="pop",
                        color="continent",
                    ),
                ),
            ]
        )

        dashboard = vm.Dashboard(pages=[page])
        Vizro().build(dashboard).run()
        ```

    === "app.yaml"

        ```yaml
        # Still requires a .py to add data to the data manager and parse YAML configuration
        # See yaml_version example
        pages:
          - components:
              - type: graph
                figure:
                  _target_: box
                  data_frame: gapminder
                  color: continent
                  x: continent
                  y: lifeExp
                  custom_data:
                    - continent
                actions:
                  - function:
                      _target_: filter_interaction
                      targets:
                        - scatter_relation_2007
              - type: graph
                id: scatter_relation_2007
                figure:
                  _target_: scatter
                  data_frame: gapminder
                  color: continent
                  x: gdpPercap
                  y: lifeExp
                  size: pop
            title: Filter interaction
        ```

    === "Result"

        [![GraphInteraction]][graphinteraction]

!!! note "`filter_interaction` with custom charts"

    If `filter_interaction` is assigned to a [custom chart](custom-charts.md), ensure that `custom_data` is an argument of the custom chart function, and that this argument is then passed to the underlying plotly function. When then adding the custom chart in `vm.Graph`, ensure that `custom_data` is passed.

    ```py
    @capture("graph")
    def my_custom_chart(data_frame, custom_data, **kwargs):
        return px.scatter(data_grame, custom_data=custom_data, **kwargs)

    ...

    vm.Graph(figure=my_custom_chart(df, custom_data=['continent'], actions=[...]))

    ```

Here is an example of how to configure a chart interaction when the source is an [`AgGrid`][vizro.models.AgGrid] component.

!!! example "AgGrid `filter_interaction`"

    === "app.py"

        ```{.python pycafe-link}
        import vizro.models as vm
        import vizro.plotly.express as px
        from vizro import Vizro
        from vizro.actions import filter_interaction
        from vizro.tables import dash_ag_grid

        df_gapminder = px.data.gapminder().query("year == 2007")

        page = vm.Page(
            title="Filter interaction",
            components=[
                vm.AgGrid(
                    figure=dash_ag_grid(data_frame=df_gapminder),
                    actions=[
                        vm.Action(function=filter_interaction(targets=["scatter_relation_2007"]))
                    ],
                ),
                vm.Graph(
                    id="scatter_relation_2007",
                    figure=px.scatter(
                        df_gapminder,
                        x="gdpPercap",
                        y="lifeExp",
                        size="pop",
                        color="continent",
                    ),
                ),
            ]
        )

        dashboard = vm.Dashboard(pages=[page])
        Vizro().build(dashboard).run()
        ```

    === "app.yaml"

        ```yaml
        # Still requires a .py to add data to the data manager and parse YAML configuration
        # See yaml_version example
        pages:
          - components:
              - type: ag_grid
                figure:
                  _target_: dash_ag_grid
                  data_frame: gapminder_2007
                actions:
                  - function:
                      _target_: filter_interaction
                      targets:
                        - scatter_relation_2007
              - type: graph
                id: scatter_relation_2007
                figure:
                  _target_: scatter
                  data_frame: gapminder_2007
                  color: continent
                  x: gdpPercap
                  y: lifeExp
                  size: pop
            title: Filter interaction
        ```

    === "Result"

        [![TableInteraction]][tableinteraction]

## Custom actions

If you require an action that isn't available as a pre-defined option, you can create a custom action function. Refer to our [user guide on custom actions](custom-actions.md) for more information.

## Chain actions

The `actions` parameter for the different screen components accepts a `list` of [`Action`][vizro.models.Action] models. This means that it's possible to chain together a list of actions that are executed by triggering only one component. The order of action execution is guaranteed, and the next action in the list will start executing only when the previous one is completed.

!!! example "Actions chaining"

    === "app.py"

        ```{.python pycafe-link extra-requirements="openpyxl"}
        import vizro.models as vm
        import vizro.plotly.express as px
        from vizro import Vizro
        from vizro.actions import export_data

        iris = px.data.iris()

        page = vm.Page(
            title="Using actions",
            components=[
                vm.Graph(
                    id="scatter",
                    figure=px.scatter(iris, x="petal_length", y="sepal_length", color="sepal_width"),
                ),
                vm.Graph(
                    id="hist",
                    figure=px.histogram(iris, x="petal_length", color="species"),
                ),
                vm.Button(
                    text="Export data",
                    actions=[
                        vm.Action(
                            function=export_data(
                                targets=["scatter"],
                            )
                        ),
                        vm.Action(
                            function=export_data(
                                targets=["hist"],
                                file_format="xlsx",
                            )
                        ),
                    ],
                ),
            ],
            controls=[
                vm.Filter(column="species"),
            ],
        )

        dashboard = vm.Dashboard(pages=[page])
        Vizro().build(dashboard).run()
        ```

    === "app.yaml"

        ```yaml
        pages:
          - components:
              - type: graph
                id: scatter
                figure:
                  _target_: scatter
                  data_frame: iris
                  color: sepal_width
                  x: petal_length
                  y: sepal_length
              - type: graph
                id: hist
                figure:
                  _target_: histogram
                  data_frame: iris
                  color: species
                  x: petal_length
              - type: button
                text: Export data
                id: export_data_button
                actions:
                  - function:
                      _target_: export_data
                      targets:
                        - scatter
                  - function:
                      _target_: export_data
                      targets:
                        - hist
                      file_format: xlsx
            controls:
              - type: filter
                column: species
            title: Exporting
        ```

    === "Result"

        [![ActionsChain]][actionschain]

[actionschain]: ../../assets/user_guides/actions/actions_chaining.png
[exportdata]: ../../assets/user_guides/actions/actions_export.png
[graphinteraction]: ../../assets/user_guides/actions/actions_filter_interaction.png
[tableinteraction]: ../../assets/user_guides/actions/actions_table_filter_interaction.png
