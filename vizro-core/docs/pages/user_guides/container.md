# How to use containers

This guide shows you how to use containers to group your page components into sections and subsections.

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
                    layout=vm.Layout(grid=[[0, 1]]),
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
