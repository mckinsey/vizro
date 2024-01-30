# How to use containers

This guide shows you how to use containers to group your components into sections and subsections within the page.

A [`Container`][vizro.models.Container] complements the concept of a [`Page`][vizro.models.Page], and the two models have almost identical arguments.
 [`Page.layout`](layouts.md) provides a way to structure the overall layout of the page, and a `Container` allows for more granular control within a specific section of that page.

While there is currently no apparent difference in rendering, additional functionality will be added to the `Container` soon (e.g. controls specific to that container),
enhancing the ability to manage related components.

## When to use containers
In general, any arbitrarily granular layout can already be achieved using [`Page.layout`](layouts.md) alone and is our
recommended approach if you just want to arrange components on a page with consistent row and/or column spacing.
However, there are a few cases where you might want to use a `Container` instead:

- If you want to split up your grid into subgrids to organize components together
- If you want to add a title to your subgrids
- If you want different row and column spacing between subgrids
- If you want to apply controls to selected subgrids (will be supported soon)


## Basic Containers
To add a [`Container`][vizro.models.Container] to your page, do the following:

1. Insert the `Container` into the `components` argument of the [`Page`][vizro.models.Page]
2. Provide a `title` to your `Container`
3. Configure your `components`, see our overview page on the various options [here](components.md)
4. (optional) Configure your `layout` , see our guide on [`Layout`](layouts.md)

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
                                iris,
                                x="sepal_length",
                                y="petal_width",
                                color="species",
                                title="Container I - Scatter"
                            )
                        ),
                        vm.Graph(
                            figure=px.bar(
                                iris,
                                x="sepal_length",
                                y="sepal_width",
                                color="species",
                                title="Container I - Bar"
                            )
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


## Nested Containers
Containers can be nested, providing a hierarchical structure for organizing components.
This nesting capability allows users to create more complex layouts and manage related components at any level of granularity.

To create nested containers, simply add a `Container` to the `components` argument of another `Container`.

!!! note

    Note that an almost identical layout can also be achieved using solely the [`Page.layout`](layouts.md) -
    see the [advanced grid example](layouts.md#grid-advanced-example) on how this can be done.

    Here we use the `Containers` instead of `Page.layout`, as we want to provide clearer visual separation between two chart groups.
    In the below example, we have two groups of charts (left and right) and want to assign separate titles to each group
    and increase the gap between them for enhanced visual separation. Such an arrangement is particularly advantageous
    when grouping charts that are thematically related.
