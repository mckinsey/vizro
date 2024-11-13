# How to use graphs

This guide shows you how to use graphs to visualize your data in the dashboard.

The [`Graph`][vizro.models.Graph] model is the most used component in many dashboards, allowing you to visualize data in a variety of ways.

To add a [`Graph`][vizro.models.Graph] to your page, do the following:

1. insert the [`Graph`][vizro.models.Graph] model into the `components` argument of the
[`Page`][vizro.models.Page] model
2. enter any of the currently available charts of the open source library [`plotly.express`](https://plotly.com/python/plotly-express/) into the `figure` argument

!!! note

    In order to use the [`plotly.express`](https://plotly.com/python/plotly-express/) chart in a Vizro dashboard, you need to import it as `import vizro.plotly.express as px`.
    This leaves any of the [`plotly.express`](https://plotly.com/python/plotly-express/) functionality untouched, but allows _direct insertion_ into the [`Graph`][vizro.models.Graph] model _as is_.

    Note also that the `plotly.express` chart needs to have a `data_frame` argument. In case you require a chart without
    a `data_frame` argument (for example, the [`imshow` chart](https://plotly.com/python/imshow/)), refer to our
    [guide on custom charts](custom-charts.md).


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
              dimensions: ["sepal_length", "sepal_width", "petal_length", "petal_width"]
            type: graph
          title: My first page
        ```
    === "Result"
        [![Graph]][Graph]

    [Graph]: ../../assets/user_guides/components/graph.png


In the Python example we directly inserted the pandas DataFrame `df` into `figure=px.scatter_matrix(df, ...)`. This is [one way to supply data to a chart](data.md#supply-directly). For the YAML version, we [refer to the data source by name](data.md#reference-by-name) as `data_frame: iris`. For a full explanation of the different methods you can use to send data to your dashboard, see [our guide to using data in Vizro](data.md).

## Customize Plotly chart

You will need to create a custom chart if you want to customize the Plotly chart beyond a function call, for example by:

* using post-update methods like `update_layout`, `update_xaxes`, `update_traces`, or
* by creating a custom `plotly.graph_objects.Figure()` object and manually adding traces with `add_trace`.

For more details, refer to our [user guide on custom chart](custom-charts.md) and the
[Plotly documentation on updating figures](https://plotly.com/python/creating-and-updating-figures/).


## Add title, header, and footer

The [`Graph`][vizro.models.Graph] accepts a `title`, `header` and `footer` argument. This is useful for providing
context to the data being displayed, or for adding a description of the data.

- **title**: Displayed as an [H3 header](https://dash.plotly.com/dash-html-components/h3), useful for summarizing the main topic or insight of the component.
- **header**: Accepts markdown text, ideal for extra descriptions, subtitles, or detailed data insights.
- **footer**: Accepts markdown text, commonly used for citing data sources, providing information on the last update, or adding disclaimers.


!!! note

    Although you can directly provide a `title` to the Plotly Express chart, we recommend using `Graph.title` for
    proper alignment with other components on the screen.

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
            type: graph
          title: Formatted Graph
        ```
    === "Result"
        [![FormattedGraph]][FormattedGraph]

    [FormattedGraph]: ../../assets/user_guides/components/formatted_graph.png
