---
description: "Use `Table` with a `dash_ag_grid` figure to display tabular data: format number, date, and string columns, disable pagination, resize columns, and apply sticky headers and styling."
---

# How to use tables

This guide shows you how to visualize tables in Vizro.

!!! tip "When to use this"

    Use [`Table`](#ag-grid) to display tabular data. For Plotly charts use [`Graph`](graph.md), for KPI tiles use a [`kpi_card` figure](figure.md#key-performance-indicator-kpi-cards), and for any other reactive Dash component use [`Figure`](figure.md).

**API reference:** [`Table`][vizro.models.Table]

Vizro visualizes tabular data using [AG Grid](#ag-grid), via the [`Table`][vizro.models.Table] model with a `dash_ag_grid` figure.

!!! note "Migrating from earlier versions"

    `Table` now supports only a `dash_ag_grid` figure. The separate `AgGrid` model and the Dash DataTable backing (`dash_data_table`) have been removed: replace `vm.AgGrid(figure=dash_ag_grid(...))` with `vm.Table(figure=dash_ag_grid(...))`, and any `dash_data_table` figure with `dash_ag_grid`. See the [migration guide](../API-reference/migration.md#aggrid-model).

## AG Grid

[AG Grid](https://www.ag-grid.com/) is an interactive table/grid component designed for viewing, editing, and exploring large datasets. It is Vizro's recommended table implementation.

The Vizro [`Table`][vizro.models.Table] model, with a `dash_ag_grid` figure, is based on the [Dash AG Grid](https://dash.plotly.com/dash-ag-grid), which is in turn based on the original [Javascript implementation](https://www.ag-grid.com/).

!!! note "More examples of AG Grid"

    If you would like to see more examples on what can be done with AG Grid, head to the [Dash AG Grid](https://dash.plotly.com/dash-ag-grid) documentation. Almost anything you see there is possible in Vizro by [creating a custom AG Grid callable](custom-tables.md).

### Basic usage

To add a [`Table`][vizro.models.Table] with a `dash_ag_grid` figure to your page, do the following:

1. Insert the [`Table`][vizro.models.Table] model into the `components` argument of the [`Page`][vizro.models.Page] model.
1. Enter the `dash_ag_grid` function under the `figure` argument (imported via `from vizro.tables import dash_ag_grid`).

The Vizro version of this AG Grid differs in one way from the original Dash AG Grid: it requires the user to pass a pandas DataFrame as the source of data. As explained in [our guide to using data in Vizro](data.md), this must be entered under the argument `data_frame`. Most other [parameters of the Dash AG Grid](https://dash.plotly.com/dash-ag-grid/reference) can be entered as keyword arguments. Note that some defaults are set for some arguments (for example, for `columnDefs`) to help with styling and usability. Sometimes a parameter may not work because it requires a callback to function. In that case you can try [creating a custom AG Grid callable](custom-tables.md).

!!! example "Basic Dash AG Grid"

    === "app.py"

        ```{.python pycafe-link hl_lines="10"}
        import vizro.models as vm
        import vizro.plotly.express as px
        from vizro import Vizro
        from vizro.tables import dash_ag_grid

        df = px.data.gapminder()

        page = vm.Page(
            title="Default Dash AG Grid",
            components=[vm.Table(figure=dash_ag_grid(data_frame=df))]
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
              - figure:
                  _target_: dash_ag_grid
                  data_frame: gapminder
                type: table
            title: Default Dash AG Grid
        ```

    === "Result"

        The dashboard renders the "Basic Dash AG Grid" example.

        [![AGGrid]][aggrid]

## Interact with other graphs and tables

An AG Grid can act as a source for [interactions with other components](graph-table-actions.md), for example to cross-filter another graph or table when the user clicks on a point.

### Disable pagination

By default, pagination is enabled in AG Grid to improve performance and usability with large datasets. If you prefer to show all rows in a single scrollable table (for example, to allow users to scroll vertically through all data), you can disable pagination by setting `dashGridOptions={"pagination": False}`.

!!! example "Dash AG Grid without pagination"

    === "app.py"

        ```{.python pycafe-link hl_lines="10"}
        import vizro.models as vm
        import vizro.plotly.express as px
        from vizro import Vizro
        from vizro.tables import dash_ag_grid

        df = px.data.gapminder()

        page = vm.Page(
            title="Dash AG Grid with pagination",
            components=[vm.Table(figure=dash_ag_grid(data_frame=df, dashGridOptions={"pagination": False}))]
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
              - figure:
                  _target_: dash_ag_grid
                  data_frame: gapminder
                  dashGridOptions:
                    pagination: false
                type: table
            title: Dash AG Grid with pagination
        ```

    === "Result"

        The dashboard renders the "Dash AG Grid without pagination" example.

        [![AGGrid]][aggrid]

### Formatting columns

#### Numbers

One of the most common tasks when working with tables is to format the columns so that displayed numbers are more readable. To do this, you can use the native functionality of [value formatters](https://dash.plotly.com/dash-ag-grid/value-formatters) or the Vizro [custom cell data types](https://dash.plotly.com/dash-ag-grid/cell-data-types#providing-custom-cell-data-types) as shown below.

The available custom cell types for Vizro are `dollar`, `euro`, `percent` and `numeric`.

To use these, define your desired `<COLUMN>` alongside the chosen `cellDataType` in the `columnDefs` argument of your `dash_ag_grid` function:

```py
columnDefs = [{"field": "<COLUMN>", "cellDataType": "euro"}]
```

In the example below we select and format some columns of the gapminder data.

!!! example "AG Grid with formatted columns"

    === "app.py"

        ```{.python pycafe-link hl_lines="8-9 18"}
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
                vm.Table(
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
        # Still requires a .py to add data to the data manager and parse YAML configuration
        # See yaml_version example
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
                type: table
            title: Example of AG Grid with formatted columns
        ```

    === "Result"

        The dashboard renders the "AG Grid with formatted columns" example.

        [![AGGrid2]][aggrid2]

#### Dates

For the [`Table`][vizro.models.Table] model to sort and filter dates correctly, the date must either be of string format `yyyy-mm-dd` (see [Dash AG Grid docs](https://dash.plotly.com/dash-ag-grid/date-filters#example:-date-filter)) or a pandas datetime object. Any pandas datetime column will be transformed into the `yyyy-mm-dd` format automatically.

#### Objects and strings

No specific formatting is available for custom objects and strings, however you can make use of [Value Formatters](https://dash.plotly.com/dash-ag-grid/value-formatters) to format displayed strings automatically.

### Resizing columns

The [`Table`][vizro.models.Table] model provides automatic column sizing options through the `columnSize` property. This feature allows you to control how columns are sized within the grid to optimize the display of your data.

You can configure column sizing by setting the `columnSize` parameter in your `dash_ag_grid` function call. By default, the `columnSize` is set to `responsiveSizeToFit` within the `vm.Table`. The available options are:

- **`autoSize`**: Automatically adjusts column widths to fit their content. This is particularly useful when you have varying content lengths and want each column to be sized appropriately for readability.

- **`sizeToFit`**: Resizes all columns proportionally to fill the entire width of the grid container. This ensures no horizontal scrolling is needed and AG Grid uses all available space.

- **`responsiveSizeToFit`**: Combines `sizeToFit` with automatic readjustment of the columns' widths when the grid container or columns change (such as when the browser window is resized or when filters are applied).

- **`None`**: Maintains the default column widths without automatic resizing.

For more advanced column sizing configurations, you can use the `columnSizeOptions` parameter in combination with `columnSize`.

!!! example "AG Grid with column sizing"

    === "app.py"

        ```{.python pycafe-link hl_lines="10"}
        import vizro.models as vm
        import vizro.plotly.express as px
        from vizro import Vizro
        from vizro.tables import dash_ag_grid

        df = px.data.gapminder()

        page = vm.Page(
            title="AG Grid with Column Sizing",
            components=[vm.Table(id="ag-grid", figure=dash_ag_grid(data_frame=df, columnSize="responsiveSizeToFit"))],
            controls=[
                vm.Parameter(
                    targets=["ag-grid.columnSize"],
                    selector=vm.RadioItems(
                        title="Select ColumnSize",
                        options=[
                            {"value": "autoSize", "label": "autoSize"},
                            {"value": "responsiveSizeToFit", "label": "responsiveSizeToFit"},
                            {"value": "sizeToFit", "label": "sizeToFit"},
                            {"value": "NONE", "label": "None"},
                        ],
                        value="responsiveSizeToFit"
                    ),
                )
            ],
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
              - figure:
                  _target_: dash_ag_grid
                  data_frame: gapminder
                  columnSize: responsiveSizeToFit
                id: ag-grid
                type: table
            controls:
              - selector:
                    # Automatically adjusts column widths
                  options: [{value: autoSize, label: autoSize},
                    # Resizes all columns proportionally
                     {value:responsiveSizeToFit: null, label: responsiveSizeToFit},
                    # Combines `sizeToFit` with automatic readjustment of the columns' widths
                     {value:sizeToFit: null, label: sizeToFit},
                    # Maintains the default column widths
                     {value: NONE, label:None: null}]
                  value: responsiveSizeToFit
                  title: Select ColumnSize
                  type: radio_items
                targets:
                  - ag-grid.columnSize
                type: parameter
            title: AG Grid with Column Sizing
        ```

    === "Result"

        The dashboard renders the "AG Grid with column sizing" example.

        [![AGGridColumnSize]][aggridcolumnsize]

For detailed information about column sizing options and advanced configurations, refer to the [Dash AG Grid column sizing documentation](https://dash.plotly.com/dash-ag-grid/column-sizing).

### Styling and changing the AG Grid

As mentioned above, all [parameters of the Dash AG Grid](https://dash.plotly.com/dash-ag-grid/reference) can be entered as keyword arguments. Below you can find an example of a styled AG Grid where some conditional formatting is applied, and where the columns are editable, but not filterable or resizable. There are more ways to alter the grid beyond this showcase. AG Grid, like any other Vizro component, can be customized using custom CSS. You can find information in the [guide to overwriting CSS properties](custom-css.md#overwrite-css-for-selected-components).

!!! example "Styled and modified Dash AG Grid"

    === "app.py"

        ```{.python pycafe-link hl_lines="8-27 29-46 55-56"}
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
                vm.Table(
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
        # Still requires a .py to add data to the data manager and parse YAML configuration
        # See yaml_version example
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
                        function: d3.format('.1f')(params.value)
                    - field: gdpPercap
                      valueFormatter:
                        function: d3.format('$,.1f')(params.value)
                      cellStyle:
                        styleConditions:
                          - condition: params.value < 1045
                            style:
                              backgroundColor: '#ff9222'
                          - condition: params.value >= 1045 && params.value <= 4095
                            style:
                              backgroundColor: '#de9e75'
                          - condition: params.value > 4095 && params.value <= 12695
                            style:
                              backgroundColor: '#aaa9ba'
                          - condition: params.value > 12695
                            style:
                              backgroundColor: '#00b4ff'
                    - field: pop
                      type: rightAligned
                      valueFormatter:
                        function: d3.format(',.0f')(params.value)
                  defaultColDef:
                    resizable: false
                    filter: false
                    editable: true
                title: Dash AG Grid
                type: table
            title: Example of a Dash AG Grid
        ```

    === "Result"

        The dashboard renders the "Styled and modified Dash AG Grid" example.

        [![AGGrid3]][aggrid3]

If the available arguments are not sufficient, there is always the option to [create a custom AG Grid callable](custom-tables.md).

#### Add sticky headers

To add sticky headers to your AG Grid, add the following CSS to your custom CSS file within your local `assets` folder.

```css
.ag-header {
    position: fixed !important;
    z-index: 1;
}

.ag-body {
    top: 40px;
}
```

If your dashboard contains multiple AG Grids, you can scope this CSS to a specific grid by assigning an ID to the corresponding `vm.Table` model and targeting it in your CSS. For example:

```css
#my-aggrid .ag-header {
    position: fixed !important;
    z-index: 1;
}

#my-aggrid .ag-body {
    top: 40px;
}
```

!!! note

    This approach works reliably only when the `Table` is positioned in the non-scrollable page.

## Add additional text

The [`Table`][vizro.models.Table] model accepts `title`, `header`, `footer` and `description` arguments. These are useful for providing additional context on the table.

- **title**: Displayed as an [H3 header](https://dash.plotly.com/dash-html-components/h3), useful for summarizing the main topic or insight of the component.
- **header**: Accepts [Markdown text](https://markdown-guide.readthedocs.io/), ideal for extra descriptions, subtitles, or detailed data insights.
- **footer**: Accepts [Markdown text](https://markdown-guide.readthedocs.io/), commonly used for citing data sources, providing information on the last update, or adding disclaimers.
- **description**: Displayed as an icon that opens a tooltip containing [Markdown text](https://markdown-guide.readthedocs.io/) when hovered over. You can provide a string to use the default info icon or a [`Tooltip`][vizro.models.Tooltip] model to use any icon from the [Google Material Icons library](https://fonts.google.com/icons).

### Formatted AG Grid

!!! example "Formatted AG Grid"

    === "app.py"

        ```{.python pycafe-link hl_lines="13-20"}

        import vizro.models as vm
        import vizro.plotly.express as px
        from vizro import Vizro
        from vizro.tables import dash_ag_grid

        gapminder_2007 = px.data.gapminder().query("year == 2007")

        page = vm.Page(
            title="Formatted AG Grid",
            components=[
                vm.Table(
                    figure=dash_ag_grid(data_frame=gapminder_2007, dashGridOptions={"pagination": True}),
                    title="Gapminder Data Insights",
                    header="""#### An Interactive Exploration of Global Health, Wealth, and Population""",
                    footer="""SOURCE: **Plotly gapminder data set, 2024**""",
                    description="""
                        The Gapminder dataset tracks the development of countries over time using indicators like life expectancy, income per person, and population size.

                        It helps reveal broad global trends, such as how health and wealth have improved in many regions, although progress hasn’t been even across all countries.
                    """,
                )
            ],
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
              - figure:
                  _target_: dash_ag_grid
                  data_frame: gapminder_2007
                  dashGridOptions:
                    pagination: true
                title: Gapminder Data Insights
                header: |
                  #### An Interactive Exploration of Global Health, Wealth, and Population
                footer: |
                  SOURCE: **Plotly gapminder data set, 2024**
                description: |
                  The Gapminder dataset tracks the development of countries over time using indicators like life expectancy, income per person, and population size.

                  It helps reveal broad global trends, such as how health and wealth have improved in many regions, although progress hasn’t been even across all countries.
                type: table
            title: Formatted AG Grid
        ```

    === "Result"

        The dashboard renders the "Formatted AG Grid" example.

        [![FormattedGrid]][formattedgrid]

[aggrid]: ../../assets/user_guides/table/aggrid.png
[aggrid2]: ../../assets/user_guides/table/formatted_aggrid.png
[aggrid3]: ../../assets/user_guides/table/styled_aggrid.png
[aggridcolumnsize]: ../../assets/user_guides/table/aggrid_columnSize.png
[formattedgrid]: ../../assets/user_guides/components/formatted_aggrid.png
