---
description: "Wrap AG Grid options with `@capture('ag_grid')` to configure grids beyond Vizro's built-in `dash_ag_grid`."
---

# How to create custom Dash AG Grids

In cases where the available arguments for the [`dash_ag_grid`][vizro.tables.dash_ag_grid] figure are not sufficient, you can create a custom Dash AG Grid.

The [`Table`][vizro.models.Table] model accepts the `figure` argument, where you can enter _any_ [`dash_ag_grid`][vizro.tables.dash_ag_grid] chart as explained in the [user guide on tables](table.md).

!!! note "More examples of AG Grid"

    If you would like to see more than the below example on what can be done with AG Grid, head to the [Dash AG Grid](https://dash.plotly.com/dash-ag-grid) documentation. Almost anything you see there is possible in Vizro by modifying the example below.

One reason to customize could be that you want to create a grid that requires computations that can be controlled by parameters. The below example shows this for the case of AG Grid.

### Steps to create a custom AG Grid

1. Define a function that returns a `dash_ag_grid.AgGrid` object.
1. Decorate it with `@capture("ag_grid")`.
1. The function must accept a `data_frame` argument (of type `pandas.DataFrame`).
1. The grid should be derived from and require only one `pandas.DataFrame`. Dataframes from other arguments will not react to dashboard controls such as [`Filter`](filters.md).
1. Pass your function to the `figure` argument of the [`Table`][vizro.models.Table] model.

The following example shows a possible version of a custom AG Grid. In this case the argument `chosen_columns` was added, which you can control with a parameter:

??? example "Custom Dash AgGrid"

    === "app.py"

        ```{.python pycafe-link hl_lines="10-29 38"}
        import vizro.models as vm
        import vizro.plotly.express as px
        from dash_ag_grid import AgGrid
        from vizro import Vizro
        from vizro.models.types import capture

        df = px.data.gapminder().query("year == 2007")


        @capture("ag_grid")
        def my_custom_aggrid(chosen_columns: list[str], data_frame=None):
            defaults = {
                "className": "ag-theme-vizro",
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
                "dashGridOptions": {
                    "theme": {"function": "vizroTheme(themeQuartz, agGrid)"},
                },
            }
            return AgGrid(
                columnDefs=[{"field": col} for col in chosen_columns], rowData=data_frame.to_dict("records"), **defaults
            )


        page = vm.Page(
            title="Example of a custom Dash AgGrid",
            components=[
                vm.Table(
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

        ```yaml
        # Still requires a .py to add data to the data manager, define CapturedCallables and parse YAML configuration
        # More explanation in the docs on `Dashboard` and extensions.
        pages:
          - components:
              - figure:
                  _target_: __main__.my_custom_aggrid
                  chosen_columns:
                    - country
                    - continent
                    - lifeExp
                    - pop
                    - gdpPercap
                  data_frame: gapminder_2007
                id: custom_ag_grid
                title: Custom Dash AgGrid
                type: table
            controls:
              - selector:
                  options:
                    - country
                    - continent
                    - lifeExp
                    - pop
                    - gdpPercap
                    - year
                  title: Choose columns
                  type: dropdown
                targets:
                  - custom_ag_grid.chosen_columns
                type: parameter
            title: Example of a custom Dash AgGrid
        ```

    === "Result"

        The dashboard renders the "Custom Dash AgGrid" example.

        [![GridCustom]][gridcustom]

## Interact with other graphs and tables

A custom AG Grid can act as a source for [interactions with other components](graph-table-actions.md), for example to cross-filter another graph or table when the user clicks on a point.

[gridcustom]: ../../assets/user_guides/table/custom_grid.png
