# How to create custom charts

This guide shows you how to create custom charts and how to add them to your dashboard. The [`Graph`][vizro.models.Graph] model accepts the `figure` argument, where you can enter _any_ [`plotly.express`](https://plotly.com/python/plotly-express/) chart as explained in the [user guide on graphs](graph.md).

## When to use a custom chart

In general, you should use the custom chart decorator `@capture("graph")` if your plotly chart needs any post-update calls or customization. For example:

- You want to use any of the post figure update calls by `plotly` such as `update_layout`, `update_xaxes`, `update_traces` (for more details, see the docs on [plotly's update calls](https://plotly.com/python/creating-and-updating-figures/#other-update-methods))
- You want to use a custom-created [`plotly.graph_objects.Figure()`](https://plotly.com/python/graph-objects/) object (in short, `go.Figure()`) and add traces yourself via [`add_trace`](https://plotly.com/python/creating-and-updating-figures/#adding-traces)

## Steps to create a custom chart

1. Define a function that returns a `go.Figure()`.
1. Decorate it with `@capture("graph")`.
1. The function must accept a `data_frame` argument (of type `pandas.DataFrame`).
1. The visualization should be derived from and require only one `pandas.DataFrame`. Dataframes from other arguments will not react to dashboard controls such as [`Filter`](filters.md).
1. Pass your function to the `figure` argument of the [`Graph`][vizro.models.Graph] model.

The minimal example below can be used as a base to build more sophisticated charts.

```py title="Minimal example of a custom chart"
from vizro.models.types import capture
import pandas as pd
import plotly.graph_objects as go

@capture("graph")
def minimal_example(data_frame:pd.DataFrame=None):
    return go.Figure()
```

Building on the above, there are several routes one can take. The following examples are guides on the most common custom requests, but also serve as an illustration of more general principles.

To alter the data in the `data_frame` argument, consider using a [Filter](filters.md) or [parametrized data loading](data.md/#parametrize-data-loading) and [dynamic data](data.md/#dynamic-data). The `data_frame` argument input to a custom chart contains the data **after** filters and parameters have been applied.

!!! note

    Custom charts can be targeted by [Filters](filters.md) or [Parameters](parameters.md) without any extra configuration. We will showcase both possibilities in the following examples.

## Enhanced `plotly.express` chart with reference line

The below examples shows a case where we enhance an existing `plotly.express` chart. We add a new argument (`hline`), that is used to draw a grey reference line at the height determined by the value of `hline`. The important thing to note is that we then add a `Parameter` that enables the dashboard user to interact with the argument, and hence move the line in this case. See the `Result` tab for an animation.

!!! example "Custom `plotly.express` scatter chart with a `Parameter`"

    === "app.py"

        ```{.python pycafe-link}
        import vizro.models as vm
        import vizro.plotly.express as px
        from vizro import Vizro
        from vizro.models.types import capture


        @capture("graph")
        def scatter_with_line(data_frame, x, y, color=None, size=None, hline=None): # (1)!
            fig = px.scatter(data_frame=data_frame, x=x, y=y, color=color, size=size)
            fig.add_hline(y=hline, line_color="gray")
            return fig


        page = vm.Page(
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

        dashboard = vm.Dashboard(pages=[page])
        Vizro().build(dashboard).run()
        ```

        1. Note that arguments of the custom chart can be parametrized. Here we choose to parametrize the `hline` argument (see below).
        1. Here we parametrize the `hline` argument, but any other argument can be parametrized as well. Since there is complete flexibility regarding what can be derived from such arguments, the dashboard user has a wide range of customization options.

    === "app.yaml"

        Custom charts are currently only possible via Python configuration.

    === "Result"

        [![Graph2]][graph2]

## New Waterfall chart based on `go.Figure()`

The below examples shows a more involved use-case. We create and style a waterfall chart, and add it alongside a filter to the dashboard. The example is based on [a plotly waterfall chart tutorial](https://plotly.com/python/waterfall-charts/).

!!! example "Custom `go.Figure()` waterfall chart with a `Parameter`"

    === "app.py"

        ```{.python pycafe-link}
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


        page = vm.Page(
            title="Custom chart",
            components=[
                vm.Graph(
                    figure=waterfall(data_frame=waterfall_data(), measure="measure", x="x", y="y", text="text"),
                ),
            ],
            controls=[
                vm.Filter(column="x", selector=vm.Dropdown(title="Financial categories")),
            ],
        )

        dashboard = vm.Dashboard(pages=[page])
        Vizro().build(dashboard).run()
        ```

    === "app.yaml"

        Custom charts are currently only possible via Python configuration.

    === "Result"

        [![Graph3]][graph3]

[graph2]: ../../assets/user_guides/custom_charts/custom_chart_showcase_parameter.gif
[graph3]: ../../assets/user_guides/custom_charts/custom_chart_waterfall.png
