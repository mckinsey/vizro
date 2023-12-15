# How to use tabs

This guide show how to effectively utilize tabs to organize and present content within your dashboard.

The [`Page`][vizro.models.Page] model accepts a `components` argument, where you can enter the [`Tabs`][vizro.models.Tabs] model. This functionality enables you to group various page components (such as [`Graph`][vizro.models.Graph], [`Table`][vizro.models.Table], [`Card`][vizro.models.Card] or [`Button`][vizro.models.Button]) under different tabs.

## Creating a Tabs model

The [`Tabs`][vizro.models.Tabs] model has `tabs` argument that accepts a list of [`Container`][vizro.models.Container] models. Each [`Container`][vizro.models.Container] visually corresponds to an individual tab within the tabbed interface.


To create and add tabs to your page, do the following steps:

1. Add the [`Tabs`][vizro.models.Tabs] model to the `components` argument of the page you are working
2. Add a list of [`Container`][vizro.models.Container] model to the `tabs` argument of the [`Tabs`][vizro.models.Tabs] model - the length of the list will be the number of tabs
3. Configure the `components` argument for every [`Container`][vizro.models.Container] model, see also our guide on [Containers](containers.md) - the title of the `Container` models will appear as title of individual tab components

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
