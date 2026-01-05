# How to use filters

This guide shows you how to add filters to your dashboard. A filter selects a subset of rows of a component's data to alter the appearance of that component. The following [components](components.md) are reactive to filters:

- [built-in graphs](graph.md) and [custom graphs](custom-charts.md)
- [built-in tables](table.md) and [custom tables](custom-tables.md)
- [built-in figures](figure.md) and [custom figures](custom-figures.md)

It is possible to add filters to a [page](pages.md) or [container](container.md#add-controls-to-container). Both the [`Page` model][vizro.models.Page] and the [`Container` model][vizro.models.Container] have an optional `controls` argument where you can give any number of controls, including filters. A filter uses the [`Filter` model][vizro.models.Filter] to filter the `data_frame` of the `figure` function of a target component model such as [`Graph`][vizro.models.Graph].

When the dashboard is running there are two ways for a user to set a filter:

- Direct user interaction with the underlying selector. For example, the user selects values from a checklist.
- [User interaction with a graph or table](graph-table-actions.md) via the [`set_control` action][vizro.actions.set_control]. This enables functionality such as [cross-filtering](graph-table-actions.md#cross-filter). To achieve a visually cleaner dashboard you might like to hide the filter's underlying selector with `visible=False`.

By default, filters that control components with [dynamic data](data.md#dynamic-data) are [dynamically updated](data.md#filters) when the underlying data changes while the dashboard is running.

## Basic filters

To add a filter to your page, do the following:

1. add the [`Filter`][vizro.models.Filter] model into the `controls` argument of the [`Page`][vizro.models.Page] model
1. configure the `column` argument, which denotes the target column to be filtered

You can also set `targets` to specify which components on the page the filter should apply to. If this is not explicitly set then `targets` defaults to all components on the page whose data source includes `column`.

!!! example "Basic Filter"

    === "app.py"

        ```{.python pycafe-link hl_lines="12-14"}
        from vizro import Vizro
        import vizro.plotly.express as px
        import vizro.models as vm

        iris = px.data.iris()

        page = vm.Page(
            title="My first page",
            components=[
                vm.Graph(figure=px.scatter(iris, x="sepal_length", y="petal_width", color="species")),
            ],
            controls=[
                vm.Filter(column="species"),
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
                  _target_: scatter
                  data_frame: iris
                  x: sepal_length
                  y: petal_width
                  color: species
                type: graph
            controls:
              - column: species
                type: filter
            title: My first page
        ```

    === "Result"

        [![Filter]][filter]

The selector is configured automatically based on the target column type data as follows:

- Categorical data uses [`vm.Dropdown(multi=True)`][vizro.models.Dropdown] where `options` is the set of unique values found in `column` across all the data sources of components in `targets`.
- [Numerical data](https://pandas.pydata.org/docs/reference/api/pandas.api.types.is_numeric_dtype.html) uses [`vm.RangeSlider`][vizro.models.RangeSlider] where `min` and `max` are the overall minimum and maximum values found in `column` across all the data sources of components in `targets`.
- [Temporal data](https://pandas.pydata.org/docs/reference/api/pandas.api.types.is_datetime64_any_dtype.html) uses [`vm.DatePicker(range=True)`][vizro.models.DatePicker] where `min` and `max` are the overall minimum and maximum values found in `column` across all the data sources of components in `targets`. A column can be converted to this type with [pandas.to_datetime](https://pandas.pydata.org/docs/reference/api/pandas.to_datetime.html).
- [Boolean data](https://pandas.pydata.org/docs/reference/api/pandas.api.types.is_bool_dtype.html) uses [`vm.Switch`][vizro.models.Switch] which provides a toggle interface for True/False values. The Switch also works with binary numerical columns containing 0/1 values.

The following example demonstrates these default selector types.

!!! example "Default Filter selectors"

    === "app.py"

        ```{.python pycafe-link hl_lines="25-28"}
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
        df_stocks_long['Is GOOG?'] = df_stocks_long["stocks"] == "GOOG"

        page = vm.Page(
            title="My first page",
            components=[
                vm.Graph(figure=px.line(df_stocks_long, x="date", y="value", color="stocks")),
            ],
            controls=[
                vm.Filter(column="stocks"),
                vm.Filter(column="value"),
                vm.Filter(column="date"),
                vm.Filter(column="Is GOOG?"),
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
              - column: Is GOOG?
                type: filter
            title: My first page
        ```

    === "Result"

        [![FilterDefault]][filterdefault]

## Change selector

If you want to have a different selector for your filter, you can give the `selector` argument of the [`Filter`][vizro.models.Filter] model a different selector model. Currently available selectors are [`Checklist`][vizro.models.Checklist], [`Dropdown`][vizro.models.Dropdown], [`RadioItems`][vizro.models.RadioItems], [`RangeSlider`][vizro.models.RangeSlider], [`Slider`][vizro.models.Slider], [`DatePicker`][vizro.models.DatePicker] and [`Switch`][vizro.models.Switch].

You can explore and test all available selectors interactively on our [feature demo dashboard](https://vizro-demo-features.hf.space/selectors).

!!! example "Filter with different selector"

    === "app.py"

        ```{.python pycafe-link hl_lines="13"}
        from vizro import Vizro
        import vizro.plotly.express as px
        import vizro.models as vm

        iris = px.data.iris()

        page = vm.Page(
            title="My first page",
            components=[
                vm.Graph(figure=px.scatter(iris, x="sepal_length", y="petal_width")),
            ],
            controls=[
                vm.Filter(column="species", selector=vm.RadioItems()),
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
                  _target_: scatter
                  data_frame: iris
                  x: sepal_length
                  y: petal_width
                type: graph
            controls:
              - column: species
                selector:
                  type: radio_items
                type: filter
            title: My first page
        ```

    === "Result"

        [![Selector]][selector]

## Further customization

For further customizations, refer to the [guide to selectors](selectors.md) and the [`Filter` model][vizro.models.Filter]. Some popular choices are:

- Select which components the filter applies to by using `targets`.
- Customize the `selector`, for example `multi` to switch between a multi-option and single-option selector, `options` for a categorical filter or `min` and `max` for a numerical filter.
- Make the filter's selector invisible by setting `visible=False`.

Below is an example where we only target one page component, and where we further customize the chosen `selector`.

!!! example "Customized Filter"

    === "app.py"

        ```{.python pycafe-link hl_lines="10 14"}
        from vizro import Vizro
        import vizro.plotly.express as px
        import vizro.models as vm

        iris = px.data.iris()

        page = vm.Page(
            title="My first page",
            components=[
                vm.Graph(id="scatter_chart", figure=px.scatter(iris, x="sepal_length", y="petal_width", color="species")),
                vm.Graph(figure=px.scatter(iris, x="petal_length", y="sepal_width", color="species")),
            ],
            controls=[
                vm.Filter(column="petal_length",targets=["scatter_chart"], selector=vm.RangeSlider(step=1)),
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
                  _target_: scatter
                  data_frame: iris
                  x: sepal_length
                  y: petal_width
                  color: species
                id: scatter_chart
                type: graph
              - figure:
                  _target_: scatter
                  data_frame: iris
                  x: petal_length
                  y: sepal_width
                  color: species
                type: graph
            controls:
              - column: petal_length
                targets:
                  - scatter_chart
                selector:
                  step: 1
                  type: range_slider
                type: filter
            title: My first page
        ```

    === "Result"

        [![Advanced]][advanced]

[advanced]: ../../assets/user_guides/control/control3.png
[filter]: ../../assets/user_guides/control/control1.png
[filterdefault]: ../../assets/user_guides/control/controls_defaults.png
[selector]: ../../assets/user_guides/control/control2.png
