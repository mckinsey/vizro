<!--

When I rewrite this page, make it clear what is difference between cross-filtering, parameter, drilldown, drillthrough. Refer to other BI tools. Make clear paradigm of control affecting components. Reference show_in_url controls. Make sure referred to from pages on graph/table and custom versions of those.

-->

# How to interact with graphs and tables

## Cross-filtering

Cross-filtering enables you to click on data in one chart or table to filter other components in the dashboard. This is enabled using the [`filter_interaction`][vizro.actions.filter_interaction] action. It can be applied to [`Graph`][vizro.models.Graph], [`Table`][vizro.models.Table], and [`AgGrid`][vizro.models.AgGrid], and is currently triggered by click.

To configure cross-filtering using `filter_interaction`, follow these steps:

1. Add the action function to the source [`Graph`][vizro.models.Graph], [`Table`][vizro.models.Table] or [`AgGrid`][vizro.models.AgGrid] component and a list of IDs of the target charts into `targets`.

```py
actions=va.filter_interaction(targets=["scatter_relation_2007"])
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

        ```{.python pycafe-link hl_lines="16 18 21"}
        import vizro.actions as va
        import vizro.models as vm
        import vizro.plotly.express as px
        from vizro import Vizro

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
                    actions=va.filter_interaction(targets=["scatter_relation_2007"]),
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
                  - type: filter_interaction
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

        ```{.python pycafe-link hl_lines="14-16 19"}
        import vizro.actions as va
        import vizro.models as vm
        import vizro.plotly.express as px
        from vizro import Vizro
        from vizro.tables import dash_ag_grid

        df_gapminder = px.data.gapminder().query("year == 2007")

        page = vm.Page(
            title="Filter interaction",
            components=[
                vm.AgGrid(
                    figure=dash_ag_grid(data_frame=df_gapminder),
                    actions=va.filter_interaction(targets=["scatter_relation_2007"]),
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
                  - type: filter_interaction
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

[graphinteraction]: ../../assets/user_guides/graph_tables_actions/actions_filter_interaction.png
[tableinteraction]: ../../assets/user_guides/graph_tables_actions/actions_table_filter_interaction.png
