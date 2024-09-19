# How to add a title, header and footer

This guide explains how to add a title, header, and footer to your components in Vizro.

The [`Graph`][vizro.models.Graph], the [`Table`][vizro.models.Table] and the [`AgGrid`][vizro.models.AgGrid] models
accept a `title`, `header` and `footer` argument. This is useful for providing context to the data being
displayed, or for adding a description of the data.

- **title**: Displayed as an [H3 header](https://dash.plotly.com/dash-html-components/h3), useful for summarizing the main topic or insight of the component.
- **header**: Accepts Markdown text, ideal for additional descriptions, subtitles, or detailed data insights.
- **footer**: Accepts Markdown text, commonly used for citing data sources, providing information on the last update, or adding disclaimers.


!!! note

    Although you can directly provide a `title` to the Plotly Express chart, we recommend using `Graph.title` for
    proper alignment with other components on the screen.

## Formatted Graph

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

## Formatted AgGrid

!!! example "Formatted AgGrid"
    === "app.py"
        ```{.python pycafe-link}

        import vizro.models as vm
        import vizro.plotly.express as px
        from vizro import Vizro
        from vizro.tables import dash_ag_grid

        gapminder_2007 = px.data.gapminder().query("year == 2007")

        page = vm.Page(
            title="Formatted AgGrid",
            components=[
                vm.AgGrid(
                    figure=dash_ag_grid(data_frame=gapminder_2007, dashGridOptions={"pagination": True}),
                    title="Gapminder Data Insights",
                    header="""#### An Interactive Exploration of Global Health, Wealth, and Population""",
                    footer="""SOURCE: **Plotly gapminder data set, 2024**""",
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
            type: ag_grid
          title: Formatted AgGrid
        ```
    === "Result"
        [![FormattedGrid]][FormattedGrid]

    [FormattedGrid]: ../../assets/user_guides/components/formatted_aggrid.png


## Formatted DataTable

!!! example "Formatted DataTable"
    === "app.py"
        ```{.python pycafe-link}

        import vizro.models as vm
        import vizro.plotly.express as px
        from vizro import Vizro
        from vizro.tables import dash_data_table

        gapminder_2007 = px.data.gapminder().query("year == 2007")

        page = vm.Page(
            title="Formatted DataTable",
            components=[
                vm.Table(
                    figure=dash_data_table(data_frame=gapminder_2007),
                    title="Gapminder Data Insights",
                    header="""#### An Interactive Exploration of Global Health, Wealth, and Population""",
                    footer="""SOURCE: **Plotly gapminder data set, 2024**""",
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
              _target_: dash_data_table
              data_frame: gapminder_2007
            title: Gapminder Data Insights
            header: |
              #### An Interactive Exploration of Global Health, Wealth, and Population
            footer: |
              SOURCE: **Plotly gapminder data set, 2024**
            type: table
          title: Formatted DataTable
        ```
    === "Result"
        [![FormattedTable]][FormattedTable]

    [FormattedTable]: ../../assets/user_guides/components/formatted_table.png
