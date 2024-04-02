# How to use tables

This guide shows you how to visualize tables in Vizro.

There are two ways to visualize tables in Vizro, using either [AG Grid](#ag-grid) or [Dash DataTable](#dash-datatable).
In general, [AG Grid](#ag-grid) is Vizro's recommended table implementation, but in some cases it may make sense to use the [Dash DataTable](#dash-datatable) instead.

## How to choose between AG Grid and Dash DataTable

Vizro offers two models - the [`AgGrid`][vizro.models.AgGrid] model and the [`Table`][vizro.models.Table] model - for the above two approaches respectively.
They both visualize tabular data in similar ways.

The main difference between the two is that the [`AgGrid`][vizro.models.AgGrid] model is based on Plotly's [Dash AG Grid](https://dash.plotly.com/dash-ag-grid) component,
while the [`Table`][vizro.models.Table] model is based on the [Dash DataTable](https://dash.plotly.com/datatable) component.

Both approaches have similar base features, and are configurable in similar ways. However, the AG Grid offers more advanced features out-of-the-box, is more customizable
and also ships a powerful enterprise version. This is why it is Vizro's recommended table implementation. At the same time, the Dash DataTable can be used if developers are
already familiar with it, or if some custom functionality is easier to implement using the Dash DataTable.


## AG Grid

[AG Grid](https://www.ag-grid.com/) is an interactive table/grid component designed for viewing, editing, and exploring large datasets. It
is Vizro's recommended table implementation.

The Vizro [`AgGrid`][vizro.models.AgGrid] model is based on the [Dash AG Grid](https://dash.plotly.com/dash-ag-grid), which is in turn based the
original [Javascript implementation](https://www.ag-grid.com/).

### Basic usage

To add a [`AgGrid`][vizro.models.AgGrid] to your page, do the following:

- Insert the [`AgGrid`][vizro.models.AgGrid] model into the `components` argument of the
[`Page`][vizro.models.Page] model.
- Enter the `dash_ag_grid` function under the `figure` argument (imported via `from vizro.tables import dash_ag_grid`).

The Vizro version of this AG Grid differs in one way from the original Dash AG Grid: it requires the user to provide a pandas dataframe as source of data.
This must be entered under the argument `data_frame`. Most other [parameters of the Dash AG Grid](https://dash.plotly.com/dash-ag-grid/reference) can be entered as keyword arguments.
Note that some defaults are set for some of the arguments (e.g. for `columnDefs`) to help with styling and usability.
In some cases a parameter may not work because it e.g. requires an additional callback to function. In that case you can try
creating a [custom AG Grid callable](custom-tables.md) or reach out to the Vizro team for help.


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
        [![AGGrid]][AGGrid]

    [AGGrid]: ../../assets/user_guides/table/aggrid.png

### Formatting columns

#### Numbers

One of the most common tasks when working with tables is to format the columns so that displayed numbers are more readable.
In order to do this, you can use the native functionality of [Value Formatters](https://dash.plotly.com/dash-ag-grid/value-formatters)
or the Vizro pre-defined [Custom Cell Data Types](https://dash.plotly.com/dash-ag-grid/cell-data-types#providing-custom-cell-data-types) as shown below.

The available custom cell types for Vizro are `dollar`, `euro`, `percentage` and `numeric`.

In order to use these, define your desired `<COLUMN>` alongside the chosen `cellDataType` in
the `columnDefs` argument of your `dash_ag_grid` function:

```py
columnDefs = [{"field": "<COLUMN>", "cellDataType": "euro"}]
```

In the example below we select and format some columns of the gapminder dataset.

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
        [![AGGrid2]][AGGrid2]

    [AGGrid2]: ../../assets/user_guides/table/formatted_aggrid.png

#### Dates

For the [`AgGrid`][vizro.models.AgGrid] model to sort and filter dates correctly, the date must either be of
string format `yyyy-mm-dd` (see [Dash AG Grid docs](https://dash.plotly.com/dash-ag-grid/date-filters#example:-date-filter))
or a pandas datetime object. Any pandas datetime column will be transformed into the `yyyy-mm-dd` format automatically.

#### Objects/Strings

No specific formatting is available for custom objects and strings, however you can make use of [Value Formatters](https://dash.plotly.com/dash-ag-grid/value-formatters)
to format e.g. displayed strings automatically.


### Styling and modifying the AG Grid

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
        [![AGGrid3]][AGGrid3]

    [AGGrid3]: ../../assets/user_guides/table/styled_aggrid.png

If the available arguments are not sufficient, there is always the option to create a [custom AG Grid callable](custom-tables.md).

## Dash DataTable

Similar to AG Grid, the [Dash DataTable](https://dash.plotly.com/datatable) is an interactive table/grid component designed for viewing, editing, and exploring large datasets.

In general, we recommend using [AG Grid](#ag-grid) for tables unless you have a particular reason to prefer Dash DataTable.

The Vizro [`Table`][vizro.models.Table] model is based on the [Dash DataTable](https://dash.plotly.com/datatable).

### Basic usage

To add a [`Table`][vizro.models.Table] to your page, do the following:

- Insert the [`Table`][vizro.models.Table] model into the `components` argument of the
[`Page`][vizro.models.Page] model.
- Enter the `dash_data_table` function under the `figure` argument (imported via `from vizro.tables import dash_data_table`).

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
                vm.Table(title="Dash DataTable", figure=dash_data_table(data_frame=df)),
            ],
        )
        dashboard = vm.Dashboard(pages=[page])

        Vizro().build(dashboard).run()
        ```
    === "app.yaml"
        ```yaml
        # Still requires a .py to register data connector in Data Manager and parse yaml configuration
        # See yaml_version example
        pages:
        - components:
          - figure:
              _target_: dash_data_table
              data_frame: gapminder_2007
            title: Dash DataTable
            type: table
          title: Example of a Dash DataTable
        ```
    === "Result"
        [![Table]][Table]

    [Table]: ../../assets/user_guides/table/table.png

### Styling and modifying the Dash DataTable

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
        )
        dashboard = vm.Dashboard(pages=[page])

        Vizro().build(dashboard).run()
        ```
    === "app.yaml"
        ```yaml
        # Still requires a .py to register data connector in Data Manager and parse yaml configuration
        # See yaml_version example
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
                type: table
            title: Dash DataTable

        ```
    === "Result"
        [![Table2]][Table2]

    [Table2]: ../../assets/user_guides/table/styled_table.png

If the available arguments are not sufficient, there is always the option to create a [custom Dash DataTable](custom-tables.md).
