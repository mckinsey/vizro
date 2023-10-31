# How to use tables

This guide shows you how to use tables to visualize your data in the dashboard.

The [`Page`][vizro.models.Page] models accepts the `components` argument, where you can enter your visual content e.g.
[`Graph`][vizro.models.Graph], [`Table`][vizro.models.Table], [`Card`][vizro.models.Card] or [`Button`][vizro.models.Button].

## Table

The [`Table`][vizro.models.Table] model allows you to visualize data in a tabular format.

To add a [`Table`][vizro.models.Table] to your page, do the following:

- insert the [`Table`][vizro.models.Table] model into the `components` argument of the
[`Page`][vizro.models.Page] model
- enter any of the currently available table functions

See below for an overview of currently supported table functions.

### Dash DataTable

The [Dash DataTable](https://dash.plotly.com/datatable) is an interactive table component designed for viewing, editing, and exploring large datasets.

You can use the [Dash DataTable](https://dash.plotly.com/datatable) in Vizro by importing
```py
from vizro.tables import dash_data_table
```
The Vizro version of this table differs in one way from the original table: it requires the user to provide a pandas dataframe as source of data.
This must be entered under the argument `data_frame`.
All other [parameters of the Dash DataTable](https://dash.plotly.com/datatable/reference) can be entered as keyword arguments. Note that we are
setting some defaults for some of the arguments to help with styling.

!!! example "Dash DataTable"
    === "app.py"
        ```py
        import vizro.models as vm
        import vizro.plotly.express as px
        from vizro import Vizro
        from vizro.tables import dash_data_table

        df = px.data.gapminder().query("year == 2007")

        page = vm.Page(
            title="Example of a Dash DataTable",
            components=[
                vm.Table(id="table", title="Dash DataTable", figure=dash_data_table(data_frame=df)),
            ],
            controls=[vm.Filter(column="continent")],
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
          - figure:
              _target_: dash_data_table
              data_frame: gapminder_2007
            title: Dash DataTable
            id: table
            type: table
          controls:
            - column: continent
              type: filter
          title: Example of a Dash DataTable
        ```
    === "Result"
        [![Table]][Table]

    [Table]: ../../assets/user_guides/table/table.png

#### Styling/Modifying the Dash DataTable

As mentioned above, all [parameters of the Dash DataTable](https://dash.plotly.com/datatable/reference) can be entered as keyword arguments. Below you can find
an example of a styled table where some conditional formatting is applied. There are many more ways to alter the table beyond this showcase.

??? example "Styled Dash DataTable"
    === "app.py"
        ```py
        import vizro.models as vm
        import vizro.plotly.express as px
        from vizro import Vizro
        from vizro.tables import dash_data_table

        df = px.data.gapminder().query("year == 2007")

        column_definitions = [
            {"name": "country", "id": "country", "type": "text", "editable": False},
            {"name": "continent", "id": "continent", "type": "text"},
            {"name": "year", "id": "year", "type": "datetime"},
            {"name": "lifeExp", "id": "lifeExp", "type": "numeric"},
            {"name": "pop", "id": "pop", "type": "numeric"},
            {"name": "gdpPercap", "id": "gdpPercap", "type": "numeric"},
        ]

        style_data_conditional = [
            {
                "if": {
                    "column_id": "year",
                },
                "backgroundColor": "dodgerblue",
                "color": "white",
            },
            {"if": {"filter_query": "{lifeExp} < 55", "column_id": "lifeExp"}, "backgroundColor": "#85144b", "color": "white"},
            {
                "if": {"filter_query": "{gdpPercap} > 10000", "column_id": "gdpPercap"},
                "backgroundColor": "green",
                "color": "white",
            },
            {"if": {"column_type": "text"}, "textAlign": "left"},
            {
                "if": {"state": "active"},
                "backgroundColor": "rgba(0, 116, 217, 0.3)",
                "border": "1px solid rgb(0, 116, 217)",
            },
        ]

        style_header_conditional = [{"if": {"column_type": "text"}, "textAlign": "left"}]

        page = vm.Page(
            title="Example of a styled Dash DataTable",
            components=[
                vm.Table(
                    id="table",
                    title="Styled table",
                    figure=dash_data_table(
                        data_frame=df,
                        columns=column_definitions,
                        sort_action="native",
                        editable=True,
                        style_data_conditional=style_data_conditional,
                        style_header_conditional=style_header_conditional,
                    ),
                ),
            ],
            controls=[vm.Filter(column="continent")],
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
              - figure:
                  _target_: dash_data_table
                  data_frame: gapminder_2007
                  sort_action: native
                  editable: true
                  columns:
                    - name: country
                      id: country
                      type: text
                      editable: false
                    - name: continent
                      id: continent
                      type: text
                    - name: year
                      id: year
                      type: datetime
                    - name: lifeExp
                      id: lifeExp
                      type: numeric
                    - name: pop
                      id: pop
                      type: numeric
                    - name: gdpPercap
                      id: gdpPercap
                      type: numeric
                  style_data_conditional:
                    - if:
                        column_id: year
                      backgroundColor: dodgerblue
                      color: white
                    - if:
                        filter_query: "{lifeExp} < 55"
                        column_id: lifeExp
                      backgroundColor: "#85144b"
                      color: white
                    - if:
                        filter_query: "{gdpPercap} > 10000"
                        column_id: gdpPercap
                      backgroundColor: green
                      color: white
                    - if:
                        column_type: text
                      textAlign: left
                    - if:
                        state: active
                      backgroundColor: rgba(0, 116, 217, 0.3)
                      border: 1px solid rgb(0, 116, 217)
                id: table
                type: table
            controls:
              - column: continent
                type: filter
            title: Dash DataTable

        ```
    === "Result"
        [![Table2]][Table2]

    [Table2]: ../../assets/user_guides/table/styled_table.png

#### Custom Table

In case you want to add custom logic to a Dash DataTable, e.g. when requiring computations that can be controlled by parameters, it is possible to
create a custom Dash DataTable in Vizro.

For this, similar to how one would create a [custom chart](../user_guides/custom_charts.md), simply do the following:

- define a function that returns a  `dash_table.DataTable` object
- decorate it with the `@capture("table")` decorator
- the function must accept a `data_frame` argument (of type `pandas.DataFrame`)
- the table should be derived from and require only one `pandas.DataFrame` (e.g. any further dataframes added through other arguments will not react to dashboard components such as `Filter`)


The following example shows a possible version of a custom table. In this case the argument `chosen_columns` was added, which you can control with a parameter:

??? example "Custom Dash DataTable"
    === "app.py"
        ```py
        from typing import List

        from dash import dash_table

        import vizro.models as vm
        import vizro.plotly.express as px
        from vizro import Vizro
        from vizro.models.types import capture

        df = px.data.gapminder().query("year == 2007")


        @capture("table")
        def my_custom_table(data_frame=None, chosen_columns: List[str] = None):
            """Custom table."""
            columns = [{"name": i, "id": i} for i in chosen_columns]
            defaults = {
                "style_as_list_view": True,
                "style_data": {"border_bottom": "1px solid var(--border-subtle-alpha-01)", "height": "40px"},
                "style_header": {
                    "border_bottom": "1px solid var(--state-overlays-selected-hover)",
                    "border_top": "1px solid var(--main-container-bg-color)",
                    "height": "32px",
                },
            }
            return dash_table.DataTable(data=data_frame.to_dict("records"), columns=columns, **defaults)


        page = vm.Page(
            title="Example of a custom Dash DataTable",
            components=[
                vm.Table(
                    id="custom_table",
                    title="Custom Dash DataTable",
                    figure=my_custom_table(
                        data_frame=df, chosen_columns=["country", "continent", "lifeExp", "pop", "gdpPercap"]
                    ),
                ),
            ],
            controls=[
                vm.Parameter(
                    targets=["custom_table.chosen_columns"],
                    selector=vm.Dropdown(title="Choose columns", options=df.columns.to_list(), multi=True),
                )
            ],
        )
        dashboard = vm.Dashboard(pages=[page])

        Vizro().build(dashboard).run()
        ```
    === "app.yaml"
        ```yaml
        # Custom tables are currently only possible via python configuration
        ```
    === "Result"
        [![Table3]][Table3]

    [Table3]: ../../assets/user_guides/table/custom_table.png
