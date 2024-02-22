# How to use AG Grids

This guide shows you how to use [AG Grid](https://www.ag-grid.com/) to visualize your tabular data in the dashboard.
It is an interactive table/grid component designed for viewing, editing, and exploring large datasets.
AG Grid is Vizro's recommended table implementation.

The Vizro [`AgGrid`][vizro.models.AgGrid] model is based on the [Dash AG Grid](https://dash.plotly.com/dash-ag-grid), which is in turn based the
original [Javascript implementation](https://www.ag-grid.com/).

## Basic usage

To add a [`AgGrid`][vizro.models.AgGrid] to your page, do the following:

- insert the [`AgGrid`][vizro.models.AgGrid] model into the `components` argument of the
[`Page`][vizro.models.Page] model
- enter the `dash_ag_grid` function under the `figure` argument (imported via `from vizro.tables import dash_ag_grid`)

The Vizro version of this AG Grid differs in one way from the original Dash AG Grid: it requires the user to provide a pandas dataframe as source of data.
This must be entered under the argument `data_frame`. All other [parameters of the Dash AG Grid](https://dash.plotly.com/dash-ag-grid/reference) can be entered as keyword arguments.
Note that some defaults are set for some of the arguments (e.g. for `columnDefs`) to help with styling and usability.


!!! example "Basic Dash AG Grid"
    === "app.py"
        ```py
        import vizro.models as vm
        import vizro.plotly.express as px
        from vizro import Vizro
        from vizro.tables import dash_ag_grid

        df = px.data.gapminder()

        page = vm.Page(
            title="Example of a Dash AG Grid",
            components=[
                vm.AgGrid(title="Dash AG Grid", figure=dash_ag_grid(data_frame=df)),
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
              _target_: dash_ag_grid
              data_frame: gapminder
            title: Dash AG Grid
            type: ag_grid
          controls:
            - column: continent
              type: filter
          title: Example of a Dash AG Grid
        ```
    === "Result"
        [![Table]][Table]

    [Table]: ../../assets/user_guides/table/table.png

## Formatting columns

### Numbers

One of the most common tasks when working with tables is to format the columns such that displayed numbers are more readable.
In order to do this, one can use the native functionality of [Value Formatters](https://dash.plotly.com/dash-ag-grid/value-formatters)
or make use of the Vizro pre-defined [Custom Cell Data Types](https://dash.plotly.com/dash-ag-grid/cell-data-types#providing-custom-cell-data-types) as shown below.

The available custom cell types for Vizro are `dollar`, `euro`, `percentage` and `numeric`.

In order to use these, define your desired `<COLUMN>` alongside the chosen `cellDataType` in
the `columnDefs` argument of your `dash_ag_grid` function:

```py
columnDefs = [{"field": "<COLUMN>", "cellDataType": "euro"}]
```

In the below example we select and format some columns of the gapminder dataset.

??? example "AG Grid with formatted columns"
    === "app.py"
        ```py
        import vizro.models as vm
        import vizro.plotly.express as px
        from vizro import Vizro
        from vizro.tables import dash_ag_grid

        df = px.data.gapminder()

        columnDefs = [{"field": "country"}, {"field": "year"}, {"field": "lifeExp", "cellDataType": "numeric"},
                      {"field": "gdpPercap", "cellDataType": "dollar"}, {"field": "pop", "cellDataType": "numeric"}]

        page = vm.Page(
            title="Example of AG Grid with formatted columns",
            components=[
                vm.AgGrid(
                    title="AG Grid with formatted columns",
                    figure=dash_ag_grid(
                        data_frame=df,
                        columnDefs=columnDefs,
                    ),
                )
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
              - figure:
                  _target_: dash_ag_grid
                  data_frame: gapminder
                  columnDefs:
                    - field: country
                    - field: year
                    - field: lifeExp
                      cellDataType: numeric
                    - field: gdpPercap
                      cellDataType: dollar
                    - field: pop
                      cellDataType: numeric
                title: AG Grid with formatted columns
                type: ag_grid
            title: Example of AG Grid with formatted columns
        ```
    === "Result"
        [![Table2]][Table2]

    [Table2]: ../../assets/user_guides/table/styled_table.png

### Dates

In order for the [`AgGrid`][vizro.models.AgGrid] model to sort and filter dates correctly, the date must either be of
string format `yyyy-mm-dd` (see [Dash AG Grid docs](https://dash.plotly.com/dash-ag-grid/date-filters#example:-date-filter))
or a pandas datetime object. Any pandas datetime column will be transformed into the `yyyy-mm-dd` format automatically.

### Objects/Strings

No specific formatting is available for custom objects and strings, however you can make use of [Value Formatters](https://dash.plotly.com/dash-ag-grid/value-formatters)
in order to format e.g. displayed strings automatically.


## Further styling and customization

As mentioned above, all [parameters of the Dash AG Grid](https://dash.plotly.com/dash-ag-grid/reference) can be entered as keyword arguments. Below you can find
an example of a styled AG Grid where some conditional formatting is applied, and where the columns are editable, but not filterable or resizable.
There are many more ways to alter the grid beyond this showcase.

??? example "Styled and modified Dash AG Grid"
    === "app.py"
        ```py
        import vizro.models as vm
        import vizro.plotly.express as px
        from vizro import Vizro
        from vizro.tables import dash_ag_grid

        df = px.data.gapminder()

        cellStyle = {
            "styleConditions": [
                {
                    "condition": "params.value < 1045",
                    "style": {"backgroundColor": "#ff9222"},
                },
                {
                    "condition": "params.value >= 1045 && params.value <= 4095",
                    "style": {"backgroundColor": "#de9e75"},
                },
                {
                    "condition": "params.value > 4095 && params.value <= 12695",
                    "style": {"backgroundColor": "#aaa9ba"},
                },
                {
                    "condition": "params.value > 12695",
                    "style": {"backgroundColor": "#00b4ff"},
                },
            ]
        }

        columnDefs = [
            {"field": "country"},
            {"field": "continent"},
            {"field": "year"},
            {
                "field": "lifeExp",
                "valueFormatter": {"function": "d3.format('.1f')(params.value)"},
            },
            {
                "field": "gdpPercap",
                "valueFormatter": {"function": "d3.format('$,.1f')(params.value)"},
                "cellStyle": cellStyle,
            },
            {
                "field": "pop",
                "valueFormatter": {"function": "d3.format(',.0f')(params.value)"},
            },
        ]

        page = vm.Page(
            title="Example of Modified Dash AG Grid",
            components=[
                vm.AgGrid(
                    title="Modified Dash AG Grid",
                    figure=dash_ag_grid(
                        data_frame=df,
                        columnDefs=columnDefs,
                        defaultColDef={"resizable": False, "filter": False, "editable": True},
                    ),
                )
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
              - figure:
                  _target_: dash_ag_grid
                  data_frame: gapminder
                  columnDefs:
                    - field: country
                    - field: continent
                    - field: year
                    - field: lifeExp
                      valueFormatter:
                        function: "d3.format('.1f')(params.value)"
                    - field: gdpPercap
                      valueFormatter:
                        function: "d3.format('$,.1f')(params.value)"
                      cellStyle:
                        styleConditions:
                          - condition: params.value < 1045
                            style:
                              backgroundColor: "#ff9222"
                          - condition: params.value >= 1045 && params.value <= 4095
                            style:
                              backgroundColor: "#de9e75"
                          - condition: params.value > 4095 && params.value <= 12695
                            style:
                              backgroundColor: "#aaa9ba"
                          - condition: params.value > 12695
                            style:
                              backgroundColor: "#00b4ff"
                    - field: pop
                      type: rightAligned
                      valueFormatter:
                        function: "d3.format(',.0f')(params.value)"
                  defaultColDef:
                    resizable: false
                    filter: false
                    editable: true
                title: Dash AG Grid
                type: ag_grid
            title: Example of a Dash AG Grid
        ```
    === "Result"
        [![Table2]][Table2]

    [Table2]: ../../assets/user_guides/table/styled_table.png

If the available arguments are not sufficient, there is always the possibility to create a [custom AG Grid callable](custom_tables.md).
