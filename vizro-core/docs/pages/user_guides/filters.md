# How to use filters

This guide shows you how to add filters to your dashboard. One main way to interact with the charts/components on your page is by filtering the underlying data. A filter selects a subset of rows of a component's underlying DataFrame which alters the appearance of that component on the page.

The [`Page`][vizro.models.Page] model accepts the `controls` argument, where you can enter a [`Filter`][vizro.models.Filter] model.
This model allows the automatic creation of selectors (e.g. Dropdown, RadioItems, Slider, ...) that let a dashboard user filter with the charts/components on the screen.


## Basic Filters

To add a filter to your page, do the following:

- add the [`Filter`][vizro.models.Filter] model into the `controls` argument of the [`Page`][vizro.models.Page] model
- configure the `column` argument, which denotes the target column to be filtered

By default, all components on a page with such a `column` present will be filtered. The selector type will be chosen
automatically based on the target column, e.g. a dropdown for categorical data or a range slider for numerical data.

!!! example "Basic Filter"
    === "app.py"
        ```py
        from vizro import Vizro
        import vizro.plotly.express as px
        import vizro.models as vm

        iris = px.data.iris()

        page = vm.Page(
            title="My first page",
            components=[
                vm.Graph(id="scatter_chart", figure=px.scatter(iris, x="sepal_length", y="petal_width", color="species")),
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
        # Still requires a .py to register data connector in Data Manager and parse yaml configuration
        # See from_yaml example
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
            controls:
              - column: species
                type: filter
            title: My first page
        ```
    === "Result"
        [![Filter]][Filter]

    [Filter]: ../../assets/user_guides/control/control1.png

## Changing Selectors

If you want to have a different selector for your filter, you can provide the `selector` argument of the [`Filter`][vizro.models.Filter] with a different selector model.
Currently available selectors are [`Checklist`][vizro.models.Checklist], [`Dropdown`][vizro.models.Dropdown], [`RadioItems`][vizro.models.RadioItems], [`RangeSlider`][vizro.models.RangeSlider] and [`Slider`][vizro.models.Slider].

!!! example "Filter with custom Selector"
    === "app.py"
        ```py
        from vizro import Vizro
        import vizro.plotly.express as px
        import vizro.models as vm

        iris = px.data.iris()

        page = vm.Page(
            title="My first page",
            components=[
                vm.Graph(id="scatter_chart", figure=px.scatter(iris, x="sepal_length", y="petal_width")),
            ],
            controls=[
                vm.Filter(column="species",selector=vm.RadioItems()),
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
                  _target_: scatter
                  data_frame: iris
                  x: sepal_length
                  y: petal_width
                id: scatter_chart
                type: graph
            controls:
              - column: species
                selector:
                  type: radio_items
                type: filter
            title: My first page
        ```
    === "Result"
        [![Selector]][Selector]

    [Selector]: ../../assets/user_guides/control/control2.png

## Further customization

For further customizations, you can always refer to the [`Filter`][vizro.models.Filter] reference. Some popular choices are:

- determine which component the filter will apply to by using `targets`
- determine what the target column type is, hence choosing the default selector by using `column_type`
- choose options of lower level components, such as the `selector` models

Below is an advanced example where we only target one page component, and where we further customize the chosen `selector`.

!!! example "Advanced Filter"
    === "app.py"
        ```py
        from vizro import Vizro
        import vizro.plotly.express as px
        import vizro.models as vm

        iris = px.data.iris()

        page = vm.Page(
            title="My first page",
            components=[
                vm.Graph(id="scatter_chart", figure=px.scatter(iris, x="sepal_length", y="petal_width", color="species")),
                vm.Graph(id="scatter_chart2", figure=px.scatter(iris, x="petal_length", y="sepal_width", color="species")),
            ],
            controls=[
                vm.Filter(column="petal_length",targets=["scatter_chart"],selector=vm.RangeSlider(step=1)),
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
                id: scatter_chart2
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
        [![Advanced]][Advanced]

    [Advanced]: ../../assets/user_guides/control/control3.png
