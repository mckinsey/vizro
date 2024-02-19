# How to create custom tables

If you want to use the [`Table`][vizro.models.Table] model to and to create a custom [table](table.md) you can create your own custom table, e.g. when requiring computations that can be controlled by parameters.

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
