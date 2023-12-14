# How to use containers

This guide demonstrates how to effectively utilize containers for visualizing and organizing your components within the dashboard.

The [`Page`][vizro.models.Page] model accepts a `components` argument, where you can enter the [`Container`][vizro.models.Container] model.
This functionality enables you to group various page components (such as `Graphs`, `Buttons`, `Cards` etc.) under distinct container titles.

## Creating a Container model

The `Container` model has a `components` argument that can incorporate any available Vizro components  ([`Graphs`][vizro.models.Graphs], [`Buttons`][vizro.models.Buttons], [`Cards`][vizro.models.Cards] etc) including the `Container` model itself, enabling the creation of nested containers for further grouping.

To create and add a container to your page, do the following steps:

1. Provide a `title` to your [`Container`][vizro.models.Container]
2. Configure your `components`, see our guides on the various options here (e.g. [Graphs](graph.md), [Tables](table.md), [Cards & Buttons](components.md)).
3. (optional) Configure your `layout` , see our guide on [Layouts](layouts.md)

!!! example "Simple container"
    === "app.py"
        ```py
        import vizro.models as vm
        import vizro.plotly.express as px
        from vizro import Vizro

        iris = px.data.iris()

        page = vm.Page(
            title="Page Title",
            components=[
                vm.Container(
                    title="Container 1 title",
                    components=[
                        vm.Graph(figure=px.scatter(iris, x="sepal_length", y="petal_width", color="species")),
                    ]
                ),
                vm.Container(
                    title="Container 2 title",
                    components=[
                        vm.Graph(figure=px.bar(iris, x="sepal_length", y="sepal_width", color="species")),
                    ]
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
                    type: graph
                type: container
                title: Container 1 title
              - components:
                  - figure:
                      _target_: scatter
                      data_frame: iris
                      x: sepal_length
                      y: petal_width
                      color: species
                    type: graph
                type: container
                title: Container 2 title
          title: Page Title
        ```
    === "Result"
        [![Page]][Page]

    [Page]: ../../assets/user_guides/pages/page_sunburst.png

## Using Container model

The [`Container`][vizro.models.Container] model can be used in two distinct ways:

1. Standalone Usage: This involves using the [`Container`][vizro.models.Container] model independently to organize page components into subsections, as demonstrated in the example above.
2. Combined with [Tabs](tabs.md) model: The `Container` model can also be used together with the `Tabs` model to facilitate the creation of tabbed content within your dashboard. See our guide on [Tabs](tabs.md).
