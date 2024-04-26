# How to use selectors

This guide highlights different selectors that can be used in a dashboard. Selectors do not serve a purpose on their own, but they enable you to change how the input is given to other models, for example, the [`Filter`][vizro.models.Filter] or the [`Parameter`][vizro.models.Parameter] model.

The [`Filter`][vizro.models.Filter] or the [`Parameter`][vizro.models.Parameter] model accept the `selector` argument, where a selector model can be entered to choose how the user should input their choices for the respective models.

## Categorical selectors

Within the categorical selectors, a clear distinction exists between multi-option and single-option selectors.
For instance, the [`Checklist`][vizro.models.Checklist] functions as a multi-option selector by default while
the [`RadioItem`][vizro.models.RadioItems] serves as a single-option selector by default. However, the
[`Dropdown`][vizro.models.Dropdown] can function as both a multi-option or single-option selector.

For more information, refer to the API reference of the selector, or the documentation of its underlying Dash component:

- [`Dropdown`][vizro.models.Dropdown] based on [`dcc.Dropdown`](https://dash.plotly.com/dash-core-components/dropdown)
- [`Checklist`][vizro.models.Checklist] based on [`dcc.Checklist`](https://dash.plotly.com/dash-core-components/checklist)
- [`RadioItems`][vizro.models.RadioItems] based on [`dcc.RadioItems`](https://dash.plotly.com/dash-core-components/radioitems)

!!! note

    When configuring the `options` of the categorical selectors, you can either provide:

    - a list of values `options = ['Value A', 'Value B', 'Value C']`
    - or a dictionary of label-value mappings `options=[{'label': 'True', 'value': True}, {'label': 'False', 'value': False}]`

    The later is required if you want to provide different display labels to your option values or in case you want to
    provide boolean values as options. In this case, you need to provide a string label for your boolean values as
    boolean values cannot be displayed properly as labels in the underlying Dash components.

## Numerical selectors

For more information, refer to the API reference of the selector, or the documentation of its underlying Dash component:

- [`Slider`][vizro.models.Slider] based on [`dcc.Slider`](https://dash.plotly.com/dash-core-components/slider)
- [`RangeSlider`][vizro.models.RangeSlider] based on [`dcc.RangeSlider`](https://dash.plotly.com/dash-core-components/rangeslider)

!!! note

    When configuring the [`Slider`][vizro.models.Slider] and the [`RangeSlider`][vizro.models.RangeSlider] with float values, and using `step` with an integer value, you may notice
    unexpected behavior, such as the drag value being outside its indicated marks.
    To our knowledge, this is a current bug in the underlying [`dcc.Slider`](https://dash.plotly.com/dash-core-components/slider) and
    [`dcc.RangeSlider`](https://dash.plotly.com/dash-core-components/rangeslider) component, which you can circumvent by adapting the `step` size accordingly.

## Temporal selectors

For more information, refer to the API reference of the selector, or the documentation of its underlying Dash component:

- [`DatePicker`][vizro.models.DatePicker] based on [`dmc.DateRangePicker`](https://www.dash-mantine-components.com/components/datepicker#daterangepicker) and [`dmc.DatePicker`](https://www.dash-mantine-components.com/components/datepicker)

!!! note

    When the [`DatePicker`][vizro.models.DatePicker] is configured with `range=True` (the default), the underlying component is `dmc.DateRangePicker`. When `range=False` the underlying component is `dmc.DatePicker`.

    When configuring the [`DatePicker`][vizro.models.DatePicker] make sure to provide your dates for `min`, `max` and `value` arguments in `"yyyy-mm-dd"` format or as `datetime` type (for example, `datetime.datetime(2024, 01, 01)`).

## Default selectors

If you don't specify a selector, a default selector is applied based on the data type of the provided column.

Default selectors for:

 - categorical data: [`Dropdown`][vizro.models.Dropdown]
 - numerical data: [`RangeSlider`][vizro.models.RangeSlider]
 - temporal data: [`DatePicker(range=True)`][vizro.models.DatePicker]

Categorical selectors can be used independently of the data type of the column being filtered.

To use numerical [`Filter`][vizro.models.Filter] selectors, the filtered column must be of `numeric` format,
indicating that [pandas.api.types.is_numeric_dtype()](https://pandas.pydata.org/docs/reference/api/pandas.api.types.is_numeric_dtype.html) must return `True` for the filtered column.

To use temporal [`Filter`][vizro.models.Filter] selectors, the filtered column must be of `datetime` format,
indicating that [pandas.api.types.is_datetime64_any_dtype()](https://pandas.pydata.org/docs/reference/api/pandas.api.types.is_datetime64_any_dtype.html) must return `True` for the filtered column.

!!! tip

    `pd.DataFrame` column types can be changed to `datetime` using [pandas.to_datetime()](https://pandas.pydata.org/docs/reference/api/pandas.to_datetime.html) or


### Example of default Filter selectors

!!! example "Default Filter selectors"
    === "app.py"
        ```py
        import pandas as pd
        from vizro import Vizro
        import vizro.plotly.express as px
        import vizro.models as vm

        df_stocks = px.data.stocks(datetimes=True)

        df_stocks_long = pd.melt(
            df_stocks,
            id_vars='date',
            value_vars=['GOOG', 'AAPL', 'AMZN', 'FB', 'NFLX', 'MSFT'],
            var_name='stocks',
            value_name='value'
        )

        df_stocks_long['value'] = df_stocks_long['value'].round(3)

        page = vm.Page(
            title="My first page",
            components=[
                vm.Graph(figure=px.line(df_stocks_long, x="date", y="value", color="stocks")),
            ],
            controls=[
                vm.Filter(column="stocks"),
                vm.Filter(column="value"),
                vm.Filter(column="date"),
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
                  _target_: line
                  data_frame: df_stocks_long
                  x: date
                  y: value
                  color: stocks
                type: graph
            controls:
              - column: stocks
                type: filter
              - column: value
                type: filter
              - column: date
                type: filter
            title: My first page
        ```
    === "Result"
        [![Filter]][Filter]

    [Filter]: ../../assets/user_guides/selectors/default_filter_selectors.png


To enhance existing selectors, see our [how-to-guide on creating custom components](custom-components.md).
