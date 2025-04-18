# How to use filters

This guide shows you how to add filters to your dashboard. One main way to interact with the charts/components on your page is by filtering the underlying data. A filter selects a subset of rows of a component's underlying DataFrame which alters the appearance of that component on the page.

The [`Page`][vizro.models.Page] model accepts the `controls` argument, where you can enter a [`Filter`][vizro.models.Filter] model. This model enables the automatic creation of [selectors](selectors.md) (for example, `Dropdown` or `RangeSlider`) that operate on the charts/components on the screen.

By default, filters that control components with [dynamic data](data.md#dynamic-data) are [dynamically updated](data.md#filters) when the underlying data changes while the dashboard is running.

## Basic filters

To add a filter to your page, do the following:

1. add the [`Filter`][vizro.models.Filter] model into the `controls` argument of the [`Page`][vizro.models.Page] model
1. configure the `column` argument, which denotes the target column to be filtered

You can also set `targets` to specify which components on the page the filter should apply to. If this is not explicitly set then `targets` defaults to all components on the page whose data source includes `column`.

!!! example "Basic Filter"

    === "app.py"

        ```{.python pycafe-link}
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

The following example demonstrates these default selector types.

!!! example "Default Filter selectors"

    === "app.py"

        ```{.python pycafe-link}
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

        [![FilterDefault]][filterdefault]

## Change selector

If you want to have a different selector for your filter, you can give the `selector` argument of the [`Filter`][vizro.models.Filter] a different selector model. Currently available selectors are [`Checklist`][vizro.models.Checklist], [`Dropdown`][vizro.models.Dropdown], [`RadioItems`][vizro.models.RadioItems], [`RangeSlider`][vizro.models.RangeSlider], [`Slider`][vizro.models.Slider], and [`DatePicker`][vizro.models.DatePicker].

!!! example "Filter with different selector"

    === "app.py"

        ```{.python pycafe-link}
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

For further customizations, you can always refer to the [`Filter` model][vizro.models.Filter] reference and the [guide to selectors](selectors.md). Some popular choices are:

- select which component the filter will apply to by using `targets`
- specify configuration of the `selector`, for example `multi` to switch between a multi-option and single-option selector, `options` for a categorical filter or `min` and `max` for a numerical filter

Below is an advanced example where we only target one page component, and where we further customize the chosen `selector`.

!!! example "Advanced Filter"

    === "app.py"

        ```{.python pycafe-link}
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

To further customize selectors, see our [how-to-guide on creating custom components](custom-components.md).

[advanced]: ../../assets/user_guides/control/control3.png
[filter]: ../../assets/user_guides/control/control1.png
[filterdefault]: ../../assets/user_guides/control/controls_defaults.png
[selector]: ../../assets/user_guides/control/control2.png
