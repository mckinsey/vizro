# How to use Actions

This guide shows you how to use `Actions`, a new concept in Vizro that is similar, but not identical to [`Callbacks`](https://dash.plotly.com/basic-callbacks) in `Dash`. Many components of a dashboard (eg. [`Graph`][vizro.models.Graph] or [`Button`][vizro.models.Button]) have an optional
`actions` argument, where you can enter the [`Action`][vizro.models.Action] model.

In a nutshell, using the [`Action`][vizro.models.Action] model together with an `action function` allows you to create complex functionality on a variety of triggers in your dashboard.
There is already a range of reusable `action functions` available.

???+ info "Overview of currently available pre-defined `action functions`"

    - [`export_data`][vizro.actions.export_data]
    - [`filter_interaction`][vizro.actions.filter_interaction]

## Pre-defined actions

To attach an action to a component, you must enter the [`Action`][vizro.models.Action] model into the component's `action` argument. You can then
add a desired pre-defined `action function` into the `function` argument of the [`Action`][vizro.models.Action].

??? note "Note on `Trigger`"
    Currently each component has one pre-defined trigger property. A trigger property is an attribute of the component that triggers a configured action (e.g. for the `Button` it is `n_click`).

The below sections are guides on how to leverage pre-defined action functions

### Export data

In order to enable downloading data, you can add the [`export_data`][vizro.actions.export_data] action function to the [`Button`][vizro.models.Button] component. Hence, as
a result, when a dashboard user now clicks the button, all data on the page will be downloaded.

!!! example "`export_data`"
    === "app.py"
        ```py
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
                            function=export_data()
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
        # Still requires a .py to register data connector in Data Manager and parse yaml configuration
        # See from_yaml example
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
            controls:
              - type: filter
                column: species
            title: Exporting
        ```
    === "Result"
        [![Graph]][Graph]

    [Graph]: ../../assets/user_guides/actions/actions_export.png

### Filter data by clicking on chart

To enable filtering when clicking on data in a (source) chart, you can add the [`filter_interaction`][vizro.actions.filter_interaction] action function to the [`Graph`][vizro.models.Graph] or [`Table`][vizro.models.Table] component. The [`filter_interaction`][vizro.actions.filter_interaction] is currently configured to be triggered on click only.

To configure this chart interaction follow the steps below:

1. Add the action function to the source [`Graph`][vizro.models.Graph] or [`Table`][vizro.models.Table] component and a list of IDs of the target charts into `targets`.
```py
actions=[vm.Action(function=filter_interaction(targets=["scatter_relation_2007"]))]
```
2. If the source chart is [`Graph`][vizro.models.Graph], enter the filter columns in the `custom_data` argument of the underlying source chart `function`.
```py
Graph(figure=px.scatter(..., custom_data=["continent"]))
```
Selecting a data point with a corresponding value of "Africa" in the continent column will result in filtering the dataset of target charts to show only entries with "Africa" in the continent column. The same applies when providing multiple columns in `custom_data`.

!!! tip
    - You can reset your chart interaction filters by refreshing the page
    - You can create a "self-interaction" by providing the source chart id as its own `target`

Here is an example of how to configure a chart interaction when the source is a [`Graph`][vizro.models.Graph] component.

!!! example "`filter_interaction`"
    === "app.py"
        ```py
        import vizro.models as vm
        import vizro.plotly.express as px
        from vizro import Vizro
        from vizro.actions import filter_interaction

        df_gapminder = px.data.gapminder().query("year == 2007")

        dashboard = vm.Dashboard(
            pages=[
                vm.Page(
                    title="Filter interaction",
                    components=[
                        vm.Graph(
                            id="bar_relation_2007",
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
                    ],
                    controls=[vm.Filter(column='continent')]
                ),
            ]
        )

        Vizro().build(dashboard).run()
        ```
    === "app.yaml"
        ```yaml
        # Still requires a .py to register data connector in Data Manager and parse yaml configuration
        # See from_yaml example
        pages:
          - components:
            - type: graph
              id: bar_relation_2007
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
            controls:
              - column: continent
                type: filter
            title: Filter interaction
        ```
    === "Result"
        [![Graph2]][Graph2]

    [Graph2]: ../../assets/user_guides/actions/actions_filter_interaction.png

Here is an example of how to configure a chart interaction when the source is a [`Table`][vizro.models.Table] component.

!!! example "`filter_interaction`"
    === "app.py"
        ```py
        import vizro.models as vm
        import vizro.plotly.express as px
        from vizro import Vizro
        from vizro.actions import filter_interaction
        from vizro.tables import dash_data_table

        df_gapminder = px.data.gapminder().query("year == 2007")

        dashboard = vm.Dashboard(
            pages=[
                vm.Page(
                    title="Filter interaction",
                    components=[
                        vm.Table(
                            figure=dash_data_table(id="dash_datatable_id", data_frame=df_gapminder),
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
                    ],
                    controls=[vm.Filter(column='continent')]
                ),
            ]
        )

        Vizro().build(dashboard).run()
        ```
    === "app.yaml"
        ```yaml
        # Still requires a .py to register data connector in Data Manager and parse yaml configuration
        # See from_yaml example
        pages:
          - components:
            - type: table
              figure:
                _target_: dash_data_table
                data_frame: gapminder_2007
                id: dash_datatable_id
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
            controls:
              - column: continent
                type: filter
            title: Filter interaction
        ```
    === "Result"
        [![Table]][Table]

    [Table]: ../../assets/user_guides/actions/actions_table_filter_interaction.png

## Predefined actions customization
Many predefined actions are customizable which helps to achieve more specific desired goal. For specific options, please
refer to the [API reference][vizro.actions] on this topic.

## Actions chaining
The `actions` parameter for the different screen components accepts a `List` of [`Action`][vizro.models.Action] models.
This means that it's possible to set a list of actions that will be executed by triggering only one component.
The order of action execution is guaranteed, and the next action in the list will start executing only when the previous one is completed.


!!! example "Actions chaining"
    === "app.py"
        ```py
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
        [![Graph3]][Graph3]

    [Graph3]: ../../assets/user_guides/actions/actions_chaining.png

## Custom actions

!!! success "Coming soon!"

!!! warning

    When creating your own custom action functions (as this is already possible without official support), you are responsible for the security of your creation. Vizro cannot guarantee
    the security of custom created action functions, so make sure you keep this in mind when publicly deploying your dashboard.
