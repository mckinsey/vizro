# How to use tabs

This guide show how to effectively utilize tabs to organize and present content within your dashboard.

In the [`Page`][vizro.models.Page] model, you can utilize the `components` argument to incorporate [`Tabs`][vizro.models.Tabs] model.

## Creating a Tabs model

`Tabs` model has `tabs` argument that accepts a list of `Container` models. Each `Container` visually corresponds to an individual tab within the tabbed interface.


To create and add tabs to your page, do the following steps:

1. Configure your `components`, see our guide on [Containers](containers.md).
2. Assign the previously configured `components` to the `tabs` argument of the [`Tabs`][vizro.models.Tabs] model. This creates the connection between your page and the organized tab structure.

!!! example "Simple tabs"
    === "app.py"
        ```py
        import vizro.models as vm
        import vizro.plotly.express as px
        from vizro import Vizro

        iris = px.data.iris()

        page = vm.Page(
            title="Page Title",
            components=[
                vm.Tabs(
                    tabs=[
                        vm.Container(
                            title="Tab 1",
                            components=[
                                vm.Graph(
                                    figure=px.scatter(
                                        iris, x="sepal_length", y="petal_width", color="species"
                                    )
                                ),
                            ]
                        ),
                        vm.Container(
                            title="Tab 2",
                            components=[
                                vm.Graph(
                                    figure=px.bar(
                                        iris, x="sepal_length", y="sepal_width", color="species"
                                    )
                                ),
                            ]
                        ),
                    ]
                )
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
            -tabs:
              - components:
                  - figure:
                      _target_: scatter
                      data_frame: iris
                      x: sepal_length
                      y: petal_width
                      color: species
                    type: graph
                type: container
                title: Tab 1
              - components:
                  - figure:
                      _target_: scatter
                      data_frame: iris
                      x: sepal_length
                      y: petal_width
                      color: species
                    type: graph
                type: container
                title: Tab 2
              type: tabs
          title: Page Title
        ```
    === "Result"
        [![Page]][Page]

    [Page]: ../../assets/user_guides/pages/page_sunburst.png

!!! note

    `title` of the `Container` models will appear as title of individual tab components
