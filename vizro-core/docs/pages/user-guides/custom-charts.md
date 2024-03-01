# How to create custom charts

This guide shows you how to create custom charts and how to add them to your dashboard.
The [`Graph`][vizro.models.Graph] model accepts the `figure` argument, where you can enter _any_ [`plotly.express`](https://plotly.com/python/plotly-express/) chart as explained in the [user guide on graphs](graph.md).

## Overview of custom charts

In general, the usage of the custom chart decorator `@capture("graph")` is required if your plotly chart requires any post-update calls or customization.

### When to use a custom chart

- If you want to use any of the post figure update calls by `plotly` e.g., `update_layout`, `update_xaxes`, `update_traces`, etc. (for more details, see the docs on [plotly's update calls](https://plotly.com/python/creating-and-updating-figures/#other-update-methods))
- If you want to use a custom-created [`plotly.graph_objects.Figure()`](https://plotly.com/python/graph-objects/) object (in short, `go.Figure()`) and add traces yourself via [`add_trace`](https://plotly.com/python/creating-and-updating-figures/#adding-traces)

### Requirements of a custom chart function

- a `go.Figure()` object is returned by the function
- the function must be decorated with the `@capture("graph")` decorator
- the function accepts a `data_frame` argument (of type `pandas.DataFrame`)
- the visualization is derived from and requires only one `pandas.DataFrame` (e.g. any further dataframes added through other arguments will not react to dashboard components such as `Filter`)

The below minimal example can be used as a base to build more sophisticated charts.

```py title="Minimal example of a custom chart"
from vizro.models.types import capture

@capture("graph")
def minimal_example(data_frame:pd.DataFrame=None):
    return go.Figure()
```

Building on the above, there are several routes one can take. The following examples are guides on the most common custom requests, but also serve as an illustration of more general principles.

!!! tip

    Custom charts can be targeted by [Filters](filters.md) or [Parameters](parameters.md) without any additional configuration. We will showcase both possibilities in the following examples. In particular the `Parameters` in combination with custom charts can be highly versatile in achieving custom functionality.


## Enhanced `plotly.express` chart with reference line

The below examples shows a case where we enhance an existing `plotly.express` chart. We add a new argument (`hline`), that is used to draw a grey reference line at the height determined by the value of `hline`. The important thing to note is that we then
add a `Parameter` that allows the dashboard user to interact with the argument, and hence move the line in this case. See the `Result` tab for an animation.

!!! example "Custom `plotly.express` scatter chart with a `Parameter`"
    === "app.py"
        ```py
        import vizro.models as vm
        import vizro.plotly.express as px
        from vizro import Vizro
        from vizro.models.types import capture


        @capture("graph")
        def scatter_with_line(data_frame, x, y, color=None, size=None, hline=None): # (1)!
            fig = px.scatter(data_frame=data_frame, x=x, y=y, color=color, size=size)
            fig.add_hline(y=hline, line_color="gray")
            return fig


        page_0 = vm.Page(
            title="Custom chart",
            components=[
                vm.Graph(
                    id="enhanced_scatter",
                    figure=scatter_with_line(
                        x="sepal_length",
                        y="sepal_width",
                        color="species",
                        size="petal_width",
                        hline=3,
                        data_frame=px.data.iris(),
                    ),
                ),
            ],
            controls=[
                vm.Parameter( # (2)!
                    targets=["enhanced_scatter.hline"],
                    selector=vm.Slider(min=2, max=5, step=1, value=3, title="Horizontal line"),
                ),
            ],
        )
        dashboard = vm.Dashboard(pages=[page_0])

        Vizro().build(dashboard).run()
        ```

        1.  Note that arguments of the custom chart can be parametrized. Here we choose to parametrize the `hline` argument (see below).
        2.  Here we parametrize the `hline` argument, but any other argument can be parametrized as well. Since there is complete flexibility regarding what can be derived from such arguments, the dashboard user has a wide range of customization options.
    === "app.yaml"
        ```yaml
        # Custom charts are currently only possible via python configuration
        ```
    === "Result"
        [![Graph2]][Graph2]

    [Graph2]: ../../assets/user_guides/custom_charts/custom_chart_showcase_parameter.gif


## New Waterfall chart based on `go.Figure()`

The below examples shows a more involved use-case. We create and style a waterfall chart, and add it alongside a filter to the dashboard. The example is based on [a plotly waterfall chart tutorial](https://plotly.com/python/waterfall-charts/).

!!! example "Custom `go.Figure()` waterfall chart with a `Parameter`"
    === "app.py"
        ```py
        import pandas as pd
        import plotly.graph_objects as go

        import vizro.models as vm
        from vizro import Vizro
        from vizro.models.types import capture


        def waterfall_data():
            return pd.DataFrame(
                {
                    "measure": ["relative", "relative", "total", "relative", "relative", "total"],
                    "x": ["Sales", "Consulting", "Net revenue", "Purchases", "Other expenses", "Profit before tax"],
                    "text": ["+60", "+80", "", "-40", "-20", "Total"],
                    "y": [60, 80, 0, -40, -20, 0],
                }
            )


        @capture("graph")
        def waterfall(data_frame, measure, x, y, text, title=None):
            fig = go.Figure()
            fig.add_traces(
                go.Waterfall(
                    measure=data_frame[measure],
                    x=data_frame[x],
                    y=data_frame[y],
                    text=data_frame[text],
                    decreasing={"marker": {"color": "#ff5267"}},
                    increasing={"marker": {"color": "#08bdba"}},
                    totals={"marker": {"color": "#00b4ff"}},
                ),
            )

            fig.update_layout(title=title)
            return fig


        page_0 = vm.Page(
            title="Custom chart",
            components=[
                vm.Graph(
                    figure=waterfall(data_frame=waterfall_data(), measure="measure", x="x", y="y", text="text"),
                ),
            ],
            controls=[
                vm.Filter(column="x", selector=vm.Dropdown(title="Financial categories", multi=True)),# (1)!
            ],
        )
        dashboard = vm.Dashboard(pages=[page_0])

        Vizro().build(dashboard).run()
        ```

        1.  Note how we are able to apply a filter to a custom chart
    === "app.yaml"
        ```yaml
        # Custom charts are currently only possible via python configuration
        ```
    === "Result"
        [![Graph3]][Graph3]

    [Graph3]: ../../assets/user_guides/custom_charts/custom_chart_waterfall.png
