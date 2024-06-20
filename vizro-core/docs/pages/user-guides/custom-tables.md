# How to create custom Dash AG Grids and Dash DataTables

In cases where the available arguments for the [`dash_ag_grid`][vizro.tables.dash_ag_grid] or [`dash_data_table`][vizro.tables.dash_data_table] models are not sufficient,
you can create a custom Dash AG Grid or Dash DataTable.

The [`Table`][vizro.models.Table] and the [`AgGrid`][vizro.models.AgGrid] model accept the `figure` argument, where you can enter
_any_ [`dash_ag_grid`][vizro.tables.dash_ag_grid] or [`dash_data_table`][vizro.tables.dash_data_table] chart as explained in the [user guide on tables](table.md).

One reason could be that you want to create a table/grid that requires computations that can be controlled by parameters (see the example below).

### Steps to create a custom table

1. Define a function that returns a `dash_ag_grid.AgGrid` or `dash_table.DataTable` object.
2. Decorate it with `@capture("ag_grid")` or `@capture("table")`.
3. The function must accept a `data_frame` argument (of type `pandas.DataFrame`).
4. The table should be derived from and require only one `pandas.DataFrame`. Dataframes from other arguments
will not react to dashboard controls such as [`Filter`](filters.md).
5. Pass your function to the `figure` argument of the [`Table`][vizro.models.Table] or  [`AgGrid`][vizro.models.AgGrid] model.

The following examples show a possible version of a custom table. In this case the argument `chosen_columns` was added, which you can control with a parameter:

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
        def my_custom_table(chosen_columns: List[str], data_frame=None):
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

??? example "Custom Dash AgGrid"
    === "app.py"
        ```py
        from typing import List

        import vizro.models as vm
        import vizro.plotly.express as px
        from dash_ag_grid import AgGrid
        from vizro import Vizro
        from vizro.models.types import capture

        df = px.data.gapminder().query("year == 2007")


        @capture("ag_grid")
        def my_custom_aggrid(chosen_columns: List[str], data_frame=None):
            """Custom ag_grid."""
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
                    selector=vm.Dropdown(title="Choose columns", options=df.columns.to_list(), multi=True),
                )
            ],
        )
        dashboard = vm.Dashboard(pages=[page])

        Vizro().build(dashboard).run()
        ```
    === "app.yaml"
        ```yaml
        # Custom Ag Grids are currently only possible via python configuration
        ```
    === "Result"
        [![GridCustom]][GridCustom]

    [GridCustom]: ../../assets/user_guides/table/custom_grid.png
