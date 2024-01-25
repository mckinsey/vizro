# How to use containers

This guide shows you how to use containers to group your components into sections and subsections within the page.

A `Container` complements the concept of a [`Page`][vizro.models.Page], and the two models have almost identical arguments.
`Page.layout` provides a way to structure the overall layout of the page, and a `Container` allows for more granular control within a specific section of that page.

While there is currently no apparent difference in rendering, additional functionality will be added to the `Container` soon (e.g. controls specific to that container),
enhancing the ability to manage related components.

## When to use containers
- If you want to organize specific components together within a page section/subsection to achieve more granular control of your layout within the `Page`
- If you want to add a title to a section/subsection of your page
- If you want to apply controls specific to a `Container` (will be supported soon)


## Containers
To add a [`Container`][vizro.models.Container] to your page, do the following:

1. Insert the [`Container`][vizro.models.Container] into the `components` argument of the [`Page`][vizro.models.Page]
2. Provide a `title` to your [`Container`][vizro.models.Container]
3. Configure your `components`, see our overview page on the various options [here](components.md)
4. (optional) Configure your `layout` , see our guide on [Layouts](layouts.md)

!!! example "Container"
    === "app.py"
        ```py

        import vizro.models as vm
        import vizro.plotly.express as px
        from vizro import Vizro

        iris = px.data.iris()

        page = vm.Page(
            title="Containers",
            components=[
                vm.Container(
                    title="Container I",
                    layout=vm.Layout(grid=[[0, 1]]),  # (1)!
                    components=[
                        vm.Graph(
                            figure=px.scatter(
                                iris, x="sepal_length", y="petal_width", color="species", title="Container I - Scatter"
                            )
                        ),
                        vm.Graph(
                            figure=px.bar(iris, x="sepal_length", y="sepal_width", color="species", title="Container I - Bar")
                        ),
                    ],
                ),
                vm.Container(
                    title="Container II",
                    components=[
                        vm.Graph(
                            figure=px.scatter(
                                iris,
                                x="sepal_width",
                                y="sepal_length",
                                color="species",
                                marginal_y="violin",
                                marginal_x="box",
                                title="Container II - Scatter",
                            )
                        ),
                    ],
                ),
            ],
        )

        dashboard = vm.Dashboard(pages=[page])

        Vizro().build(dashboard).run()
        ```

        1.  If you don't specify `layout`, it will default to `[[0], [1]]`, meaning the components will be arranged in rows.

    === "app.yaml"
        ```yaml
        # Still requires a .py to register data connector in Data Manager and parse yaml configuration
        # See from_yaml example
        pages:
          - components:
              - components:
                  - figure:
                      _target_: scatter
                      data_frame: iris
                      x: sepal_length
                      y: petal_width
                      color: species
                      title: Container I - Scatter
                    type: graph
                  - figure:
                      _target_: bar
                      data_frame: iris
                      x: sepal_length
                      y: petal_width
                      color: species
                      title: Container I - Bar
                    type: graph
                layout:
                  grid: [[0, 1]]
                type: container
                title: Container I
              - components:
                  - figure:
                      _target_: scatter
                      data_frame: iris
                      x: sepal_width
                      y: sepal_length
                      color: species
                      marginal_y: violin
                      marginal_x: box
                      title: Container II - Scatter
                    type: graph
                type: container
                title: Container II
            title: Containers
        ```
    === "Result"
        [![Container]][Container]

    [Container]: ../../assets/user_guides/components/containers.png


## Nested containers
Containers can be nested, providing a hierarchical structure for organizing components.
This nesting capability allows users to create more complex layouts and manage related components at any level of granularity.

To create nested containers, simply add a `Container` to the `components` argument of another `Container`.

!!! example "Nested Containers"
    === "app.py"
        ```py

        import vizro.models as vm
        import vizro.plotly.express as px
        from vizro import Vizro

        df = px.data.gapminder()

        nested_container_one = vm.Container(
            title="Nested Container I",
            layout=vm.Layout(grid=[[0, 1], [2, 2]]),
            components=[
                vm.Graph(
                    figure=px.line(
                        df,
                        title="Graph 1 - Nested Container I",
                        x="year",
                        y="lifeExp",
                        color="continent",
                    ),
                ),
                vm.Graph(
                    figure=px.scatter(
                        df,
                        title="Graph 2 - Nested Container I",
                        x="gdpPercap",
                        y="lifeExp",
                        size="pop",
                        color="continent",
                    ),
                ),
                vm.Graph(
                    figure=px.box(
                        df,
                        title="Graph 3 - Nested Container I",
                        x="continent",
                        y="lifeExp",
                        color="continent",
                    ),
                ),
            ],
        )

        nested_container_two = vm.Container(
            title="Nested Container II",
            layout=vm.Layout(grid=[[0, 1]]),
            components=[
                vm.Graph(
                    figure=px.line(
                        df,
                        title="Graph 4 - Nested Container II",
                        x="year",
                        y="lifeExp",
                        color="continent",
                    ),
                ),
                vm.Graph(
                    figure=px.scatter(
                        df,
                        title="Graph 5 - Nested Container II",
                        x="gdpPercap",
                        y="lifeExp",
                        size="pop",
                        color="continent",
                    ),
                ),
            ],
        )

        page = vm.Page(
            title="Nested Containers",
            components=[
                vm.Container(
                    title="Container Title",
                    layout=vm.Layout(grid=[[0, 1]], col_gap="80px"),
                    components=[nested_container_one, nested_container_two],
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
              - components:
                  - components:
                      - figure:
                          _target_: line
                          data_frame: gapminder
                          x: year
                          y: lifeExp
                          color: continent
                          title: Graph 1 - Nested Container I
                        type: graph
                      - figure:
                          _target_: scatter
                          data_frame: gapminder
                          x: gdpPercap
                          y: lifeExp
                          size: pop
                          color: continent
                          title: Graph 2 - Nested Container I
                        type: graph
                      - figure:
                          _target_: box
                          data_frame: gapminder
                          x: continent
                          y: lifeExp
                          color: continent
                          title: Graph 3 - Nested Container I
                        type: graph
                    layout:
                      grid: [[ 0, 1 ], [2, 2]]
                    type: container
                    title: Nested Container I
                  - components:
                      - figure:
                          _target_: line
                          data_frame: gapminder
                          x: year
                          y: lifeExp
                          color: continent
                          title: Graph 4 - Nested Container II
                        type: graph
                      - figure:
                          _target_: scatter
                          data_frame: gapminder
                          x: gdpPercap
                          y: lifeExp
                          size: pop
                          color: continent
                          title: Graph 5 - Nested Container II
                        type: graph
                    layout:
                      grid: [[ 0, 1 ]]
                    type: container
                    title: Nested Container I
                layout:
                  grid: [[0, 1]]
                  col_gap: 80px
                type: container
                title: Container Title
            title: Nested Containers
        ```
    === "Result"
        [![NestedContainer]][NestedContainer]

    [Container]: ../../assets/user_guides/components/nested_containers.png
