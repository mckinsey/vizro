# How to use graphs

This guide shows you how to use graphs to visualize your data in the dashboard.

The [`Graph`][vizro.models.Graph] model is the most used component in many dashboards, allowing you to visualize data in a variety of ways. It is based on [`dcc.Graph`](https://dash.plotly.com/dash-core-components/graph).

To add a [`Graph`][vizro.models.Graph] to your page, do the following:

1. insert the [`Graph`][vizro.models.Graph] model into the `components` argument of the [`Page`][vizro.models.Page] model
1. enter any of the currently available charts of the open source library [`plotly.express`](https://plotly.com/python/plotly-express/) into the `figure` argument

!!! note

    To use the [`plotly.express`](https://plotly.com/python/plotly-express/) chart in a Vizro dashboard, you need to import it as `import vizro.plotly.express as px`. This leaves any of the [`plotly.express`](https://plotly.com/python/plotly-express/) functionality untouched yet enables _direct insertion_ into the [`Graph`][vizro.models.Graph] model _as is_.

    Note also that the `plotly.express` chart needs to have a `data_frame` argument. In case you require a chart without a `data_frame` argument (for example, the [`imshow` chart](https://plotly.com/python/imshow/)), refer to our [guide on custom charts](custom-charts.md).

## Insert Plotly chart

!!! example "Graph"

    === "app.py"

        ```{.python pycafe-link}
        import vizro.models as vm
        import vizro.plotly.express as px
        from vizro import Vizro

        df = px.data.iris()

        page = vm.Page(
            title="My first page",
            components=[
                vm.Graph(
                    figure=px.scatter_matrix(
                        df, dimensions=["sepal_length", "sepal_width", "petal_length", "petal_width"], color="species"
                    ),
                ),
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
                  _target_: scatter_matrix
                  color: species
                  data_frame: iris
                  dimensions: [sepal_length, sepal_width, petal_length, petal_width]
                type: graph
            title: My first page
        ```

    === "Result"

        [![Graph]][graph]

In the Python example we directly inserted the pandas DataFrame `df` into `figure=px.scatter_matrix(df, ...)`. This is [one way to supply data to a chart](data.md#supply-directly). For the YAML version, we [refer to the data source by name](data.md#reference-by-name) as `data_frame: iris`. For a full explanation of the different methods you can use to send data to your dashboard, see [our guide to using data in Vizro](data.md).

## Customize Plotly chart

You will need to create a custom chart if you want to customize the Plotly chart beyond a function call, for example by:

- using post-update methods like `update_layout`, `update_xaxes`, `update_traces`, or
- by creating a custom `plotly.graph_objects.Figure()` object and manually adding traces with `add_trace`.

For more details, refer to our [user guide on custom chart](custom-charts.md) and the [Plotly documentation on updating figures](https://plotly.com/python/creating-and-updating-figures/).

## Add additional text

The [`Graph`][vizro.models.Graph] model accepts `title`, `header`, `footer` and `description` arguments. These are useful for providing additional context on the chart.

- **title**: Displayed as an [H3 header](https://dash.plotly.com/dash-html-components/h3), useful for summarizing the main topic or insight of the component.
- **header**: Accepts [Markdown text](https://markdown-guide.readthedocs.io/), ideal for extra descriptions, subtitles, or detailed data insights.
- **footer**: Accepts [Markdown text](https://markdown-guide.readthedocs.io/), commonly used for citing data sources, providing information on the last update, or adding disclaimers.
- **description**: Displayed as an icon that opens a tooltip containing [Markdown text](https://markdown-guide.readthedocs.io/) when hovered over. You can provide a string to use the default info icon or a [`Tooltip`][vizro.models.Tooltip] model to use any icon from the [Google Material Icons library](https://fonts.google.com/icons).

!!! note "Use `Graph.title` instead of the Plotly Express chart title"

    Although you can directly give a `title` to the Plotly Express chart, we recommend using `Graph.title` for proper alignment with other components on the screen.

!!! example "Formatted Graph"

    === "app.py"

        ```{.python pycafe-link}

        import vizro.models as vm
        import vizro.plotly.express as px
        from vizro import Vizro

        iris = px.data.iris()

        page = vm.Page(
            title="Formatted Graph",
            components=[
                vm.Graph(
                    figure=px.scatter(iris, x="sepal_width", y="sepal_length", color="species"),
                    title="Relationships between Sepal Width and Sepal Length",
                    header="""
                        Each point in the scatter plot represents one of the 150 iris flowers, with colors indicating their
                        types. The Setosa type is easily identifiable by its short and wide sepals.

                        However, there is still overlap between the Versicolor and Virginica types when considering only sepal
                        width and length.
                        """,
                    footer="""SOURCE: **Plotly iris data set, 2024**""",
                    description="""
                        The Iris dataset includes measurements of 150 iris flowers across three types: Setosa, Versicolor, and Virginica.

                        While all samples are labeled by type, they can appear similar when looking at just some features. It's a useful dataset for exploring patterns and challenges in classification.
                    """,
                ),
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
                  x: sepal_width
                  y: sepal_length
                  color: species
                  data_frame: iris
                title: Relationships between Sepal Width and Sepal Length
                header: |
                  Each point in the scatter plot represents one of the 150 iris flowers, with colors indicating their
                  types. The Setosa type is easily identifiable by its short and wide sepals.

                  However, there is still overlap between the Versicolor and Virginica types when considering only sepal
                  width and length.
                footer: |
                  SOURCE: **Plotly iris data set, 2024**
                description: |
                  The Iris dataset includes measurements of 150 iris flowers across three types: Setosa, Versicolor, and Virginica.

                  While all samples are labeled by type, they can appear similar when looking at just some features. It's a useful dataset for exploring patterns and challenges in classification.
                type: graph
            title: Formatted Graph
        ```

    === "Result"

        [![FormattedGraph]][formattedgraph]

## The `extra` argument

The `Graph` is based on the underlying Dash component [`dcc.Graph`](https://dash.plotly.com/dash-core-components/graph/). Using the `extra` argument you can pass extra arguments to `dcc.Graph` in order to alter it beyond the chosen defaults.

!!! note

    Using `extra` is a quick and flexible way to alter a component beyond what Vizro offers. However, [it is not a part of the official Vizro schema](../explanation/schema.md#what-is-the-vizro-json-schema) and the underlying implementation details may change. If you want to guarantee that your apps keep running, we recommend that you pin your Vizro version.

An example use would be to [remove the plotly mode bar](https://plotly.com/python/configuration-options/#preventing-the-modebar-from-appearing). For this, you can use `extra={"config": {"displayModeBar": False}}`.

!!! example "Graph with extra"

    === "app.py"

        ```{.python pycafe-link}

        import vizro.models as vm
        import vizro.plotly.express as px
        from vizro import Vizro

        iris = px.data.iris()

        page = vm.Page(
            title="Graph without ModeBar",
            components=[
                vm.Graph(
                    figure=px.scatter(iris, x="sepal_width", y="sepal_length", color="species"),
                    title="Relationships between Sepal Width and Sepal Length",
                    extra={"config": {"displayModeBar": False}},
                ),
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
                  x: sepal_width
                  y: sepal_length
                  color: species
                  data_frame: iris
                title: Relationships between Sepal Width and Sepal Length
                extra:
                  config:
                    displayModeBar: false
                type: graph
            title: Graph without ModeBar
        ```

    === "Result"

        [![GraphWithExtra]][graphwithextra]

[formattedgraph]: ../../assets/user_guides/components/formatted_graph.png
[graph]: ../../assets/user_guides/components/graph.png
[graphwithextra]: ../../assets/user_guides/components/graph_with_extra.png
