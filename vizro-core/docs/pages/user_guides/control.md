# How to use controls

This guide shows you how to add controls to your dashboard. The main way to interact with the charts/components on your page is by filtering the underlying data or by changing the parameters of the underlying function.

The [`Page`][vizro.models.Page] model accepts the `controls` argument, where you can enter either a [`Filter`][vizro.models.Filter] or a [`Parameter`][vizro.models.Parameter] model. Both these models allow the automatic creation of selectors (e.g. Dropdown, RadioItems, Slider, ...) that let a dashboard user interact with the charts/components on the screen.

## Filters

Filters are one of the main ways to interact with a chart/component in a dashboard. A filter selects a subset or rows of a component's underlying DataFrame which alters the appearance of that component on the page.

### Basic Filters

You can add a filter to your page by adding the [`Filter`][vizro.models.Filter] model into the `controls` argument of the [`Page`][vizro.models.Page] model. [`Filter`][vizro.models.Filter] requires only the `column` argument, which denotes the target column to be filtered. By default, all components on a page with such a column present will be filtered. The selector type will be chosen automatically based on the target column, a dropdown for categorical data, a range slider for numerical data.

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
        # Still requires a .py to register data connector in Data Manager and parse yaml configuration - see from_yaml example
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

### Changing Selectors

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

### Further customization

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

## Parameters

Parameters are another convenient way to interact with a chart/component in a dashboard. A parameter essentially let's you alter the arguments of the underlying function that produces the target chart/component.

### Basic Parameters

You can add a parameter to your page by adding the [`Parameter`][vizro.models.Parameter] model into the `controls` argument of the [`Page`][vizro.models.Page] model. [`Parameter`][vizro.models.Parameter] requires the `targets` argument and the `selector` argument.

In the `targets` argument, you can specify the component and function argument that the parameter should be applied to in the form of `<target_component_id>.<target_argument>` (eg. `scatter_chart.title`).

Unlike for the [`Filter`][vizro.models.Filter] model, you also have to configure the `selector` argument, by providing it with an appropriate model and the desired options/numeric ranges.

!!! example "Basic Parameter"
    === "app.py"
        ```py
        from vizro import Vizro
        import vizro.plotly.express as px
        import vizro.models as vm

        iris = px.data.iris()

        page = vm.Page(
            title="My first page",
            components=[
                vm.Graph(
                    id="scatter_chart",
                    figure=px.scatter(iris, title="My scatter chart", x="sepal_length", y="petal_width", color="species"),
                ),
            ],
            controls=[
                vm.Parameter(
                    targets=["scatter_chart.title"],
                    selector=vm.Dropdown(
                        options=["My scatter chart", "A better title!", "Another title..."],
                        multi=False,
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
              - selector:
                  options: ["My scatter chart", "A better title!", "Another title..."]
                  multi: False
                  type: dropdown
                targets:
                  - scatter_chart.title
                type: parameter
            title: My first page
        ```
    === "Result"
        [![Parameter]][Parameter]

    [Parameter]: ../../assets/user_guides/control/control4.png

### Nested Parameters

If you want to modify nested parameters, you can specify the `targets` argument with a comma separated string like `<target_component_id>.<target_argument>.<first_hierarchy>`.

!!! example "Nested Parameters for multiple targets"
    === "app.py"
        ```py
        from vizro import Vizro
        import vizro.plotly.express as px
        import vizro.models as vm

        iris = px.data.iris()

        page = vm.Page(
            title="My first page",
            components=[
                vm.Graph(
                    id="scatter_chart",
                    figure=px.scatter(
                        iris,
                        x="sepal_width",
                        y="sepal_length",
                        color="species",
                        size="petal_length",
                        color_discrete_map={"setosa": "#00b4ff", "versicolor": "#ff9222"},
                    ),
                ),
                vm.Graph(
                    id="bar_chart",
                    figure=px.bar(
                        iris,
                        x="sepal_width",
                        y="sepal_length",
                        color="species",
                        color_discrete_map={"setosa": "#00b4ff", "versicolor": "#ff9222"},
                    ),
                ),
            ],
            controls=[
                vm.Parameter(
                    targets=["scatter_chart.color_discrete_map.virginica", "bar_chart.color_discrete_map.virginica"],
                    selector=vm.Dropdown(
                        options=["#ff5267", "#3949ab"],
                        multi=False,
                        value="#3949ab",
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
        # See from_yaml example
        pages:
          - components:
              - figure:
                  _target_: scatter
                  data_frame: iris
                  x: sepal_width
                  y: sepal_length
                  size: petal_length
                  color: species
                  color_discrete_map: {"setosa": "#00b4ff", "versicolor": "#ff9222"}
                id: scatter_chart
                type: graph
              - figure:
                  _target_: bar
                  data_frame: iris
                  x: sepal_width
                  y: sepal_length
                  color: species
                  color_discrete_map: {"setosa": "#00b4ff", "versicolor": "#ff9222"}
                id: bar_chart
                type: graph
            controls:
              - selector:
                  options: ["#ff5267", "#3949ab"]
                  value: #3949ab
                  multi: False
                  type: dropdown
                targets: ["scatter_chart.color_discrete_map.virginica", "bar_chart.color_discrete_map.virginica"]
                type: parameter
            title: My first page
        ```
    === "Result"
        [![Nested]][Nested]

    [Nested]: ../../assets/user_guides/control/control5.png

In the above example, the object passed to the function argument `color_discrete_map` is a dictionary which maps the different flower species to fixed colors (eg. `{"virginica":"blue"}`). In this case we do not want to change the entire dictionary, but only the value `blue`. We do this by specifying a target as `scatter.color_discrete_map.virginica`.

Note that in the above example we also have one parameter affect multiple targets.


## Selectors

### Categorical Selectors
Within the categorical selectors, a clear distinction exists between multi-option and single-option selectors.
For instance, the [`Checklist`][vizro.models.Checklist] functions as a multi-option selector by default while
the [`RadioItem`][vizro.models.RadioItems] serves as a single-option selector by default. However, the
[`Dropdown`][vizro.models.Dropdown] can function as both a multi-option or single-option selector.

For more details, kindly refer to the documentation of the underlying dash components:

- [dcc.Dropdown](https://dash.plotly.com/dash-core-components/dropdown)
- [dcc.Checklist](https://dash.plotly.com/dash-core-components/checklist)
- [dcc.RadioItems](https://dash.plotly.com/dash-core-components/radioitems)

???+ note

    When configuring the `options` of the categorical selectors, you can either provide:

    - a list of values e.g. `options = ['Value A', 'Value B', 'Value C']`
    - or a dictionary of label-value mappings e.g. `options=[{'label': 'True', 'value': True}, {'label': 'False', 'value': False}]`

    The later is required if you want to provide different display labels to your option values or in case you want to
    provide boolean values as options. In this case, you need to provide a string label for your boolean values as
    boolean values cannot be displayed properly as labels in the underlying dash components.

### Numerical Selectors

For more details, kindly refer to the documentation of the underlying dash components:

- [dcc.Slider](https://dash.plotly.com/dash-core-components/slider])
- [dcc.RangeSlider](https://dash.plotly.com/dash-core-components/rangeslider])

???+ note

    When configuring the [`Slider`][vizro.models.Slider] and the [`RangeSlider`][vizro.models.RangeSlider] with float values, and using `step` with an integer value, you may notice
    unexpected behavior, such as the drag value being outside its indicated marks.
    To our knowledge, this is a current bug in the underlying [`dcc.Slider`](https://dash.plotly.com/dash-core-components/slider) and
    [`dcc.RangeSlider`](https://dash.plotly.com/dash-core-components/rangeslider) component, which you can circumvent by adapting the `step` size accordingly.

To enhance existing selectors, please see our How-to-guide on creating [custom components](custom_components.md)
