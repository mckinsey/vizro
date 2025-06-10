# How to create custom Dash AG Grids and Dash DataTables

In cases where the available arguments for the [`dash_ag_grid`][vizro.tables.dash_ag_grid] or [`dash_data_table`][vizro.tables.dash_data_table] models are not sufficient, you can create a custom Dash AG Grid or Dash DataTable.

The [`Table`][vizro.models.Table] and the [`AgGrid`][vizro.models.AgGrid] model accept the `figure` argument, where you can enter _any_ [`dash_ag_grid`][vizro.tables.dash_ag_grid] or [`dash_data_table`][vizro.tables.dash_data_table] chart as explained in the [user guide on tables](table.md).

!!! note "More examples of AG Grid"

    If you would like to see more than the below examples on what can be done with AG Grid and Dash DataTables, head to the [Dash AG Grid](https://dash.plotly.com/dash-ag-grid) and [Dash DataTable](https://dash.plotly.com/datatable) documentation respectively. Almost anything you see there is possible in Vizro by modifying the examples below.

One reason to customize could be that you want to create a table/grid that requires computations that can be controlled by parameters. The below example shows this for the case of AG Grid and Dash DataTable.

### Steps to create a custom table

1. Define a function that returns a `dash_ag_grid.AgGrid` or `dash_table.DataTable` object.
1. Decorate it with `@capture("ag_grid")` or `@capture("table")`.
1. The function must accept a `data_frame` argument (of type `pandas.DataFrame`).
1. The table should be derived from and require only one `pandas.DataFrame`. Dataframes from other arguments will not react to dashboard controls such as [`Filter`](filters.md).
1. Pass your function to the `figure` argument of the [`Table`][vizro.models.Table] or [`AgGrid`][vizro.models.AgGrid] model.

The following examples show a possible version of a custom table. In this case the argument `chosen_columns` was added, which you can control with a parameter:

??? example "Custom Dash DataTable"

    === "app.py"

        ```{.python pycafe-link}
        from dash import dash_table

        import vizro.models as vm
        import vizro.plotly.express as px
        from vizro import Vizro
        from vizro.models.types import capture

        df = px.data.gapminder().query("year == 2007")


        @capture("table")
        def my_custom_table(chosen_columns: list[str], data_frame=None):
            columns = [{"name": i, "id": i} for i in chosen_columns]
            defaults = {
                "style_as_list_view": True,
                "style_data": {"border_bottom": "1px solid var(--border-subtleAlpha01)", "height": "40px"},
                "style_header": {
                    "border_bottom": "1px solid var(--stateOverlays-selectedHover)",
                    "border_top": "None",
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
                    selector=vm.Dropdown(title="Choose columns", options=df.columns.to_list()),
                )
            ],
        )

        dashboard = vm.Dashboard(pages=[page])
        Vizro().build(dashboard).run()
        ```

    === "app.yaml"

        Custom tables are currently only possible via Python configuration.

    === "Result"

        [![Table3]][table3]

??? example "Custom Dash AgGrid"

    === "app.py"

        ```{.python pycafe-link}
        import vizro.models as vm
        import vizro.plotly.express as px
        from dash_ag_grid import AgGrid
        from vizro import Vizro
        from vizro.models.types import capture

        df = px.data.gapminder().query("year == 2007")


        @capture("ag_grid")
        def my_custom_aggrid(chosen_columns: list[str], data_frame=None):
            defaults = {
                "className": "ag-theme-quartz-dark ag-theme-vizro",
                "defaultColDef": {
                    "resizable": True,
                    "sortable": True,
                    "filter": True,
                    "filterParams": {
                        "buttons": ["apply", "reset"],
                        "closeOnApply": True,
                    },
                    "flex": 1,
                    "minWidth": 70,
                },
                "style": {"height": "100%"},
            }
            return AgGrid(
                columnDefs=[{"field": col} for col in chosen_columns], rowData=data_frame.to_dict("records"), **defaults
            )


        page = vm.Page(
            title="Example of a custom Dash AgGrid",
            components=[
                vm.AgGrid(
                    id="custom_ag_grid",
                    title="Custom Dash AgGrid",
                    figure=my_custom_aggrid(
                        data_frame=df, chosen_columns=["country", "continent", "lifeExp", "pop", "gdpPercap"]
                    ),
                ),
            ],
            controls=[
                vm.Parameter(
                    targets=["custom_ag_grid.chosen_columns"],
                    selector=vm.Dropdown(title="Choose columns", options=df.columns.to_list()),
                )
            ],
        )

        dashboard = vm.Dashboard(pages=[page])
        Vizro().build(dashboard).run()
        ```

    === "app.yaml"

        Custom Ag Grids are currently only possible via Python configuration.

    === "Result"

        [![GridCustom]][gridcustom]

[gridcustom]: ../../assets/user_guides/table/custom_grid.png
[table3]: ../../assets/user_guides/table/custom_table.png
