# How to use containers

This guide shows you how to use containers to group your components into sections and subsections within the page.

A [`Container`][vizro.models.Container] complements the idea of a [`Page`][vizro.models.Page], and the two models have almost identical arguments.
 [`Page.layout`](layouts.md) offers a way to structure the overall layout of the page, and a `Container` enables more granular control within a specific section of that page.

While there is currently no clear difference in rendering, extra functionality will be added to the `Container` soon (including controls specific to that container),
enhancing the ability to manage related components.

??? note "Displaying multiple containers inside Tabs"

    An alternative way for displaying multiple containers on one page is to place them inside [Tabs](tabs.md).

    [`Tabs`][vizro.models.Tabs] organize and separate groups of related content in a dashboard, letting users switch between different sections or views.
    They are a way of putting multiple containers into the same screen space, and letting the user switch between them.

    ![tabs](../../assets/user_guides/components/tabs-info.png){ width="500" }



## When to use containers
In general, any arbitrarily granular layout can already be achieved by [using `Page.layout`](layouts.md) alone and is our
recommended approach if you want to arrange components on a page with consistent row and/or column spacing.

`Page.layout` has a `grid` argument that sets the overall layout of the page.
`Container.layout` also has a `grid` argument. This enables you to insert a further `grid` into a component's space on the page,
enabling more granular control by breaking the overall page grid into subgrids.

Here are a few cases where you might want to use a `Container` instead of `Page.layout`:

- If you want to split up your grid into subgrids to organize components together
- If you want to add a title to your subgrids
- If you want different row and column spacing between subgrids
- If you want to apply controls to selected subgrids (will be supported soon)


## Basic containers
To add a [`Container`][vizro.models.Container] to your page, do the following:

1. Insert the `Container` into the `components` argument of the [`Page`][vizro.models.Page]
2. Set a `title` for your `Container`
3. Configure your `components`, [read the overview page for various options](components.md)
4. (optional) Configure your `layout`, see [the guide on `Layout`](layouts.md)

!!! example "Container"
    === "app.py"
        ```py

        import vizro.models as vm
        import vizro.plotly.express as px
        from vizro import Vizro

        iris = px.data.iris()

        page = vm.Page(
            title="Containers",
            components=[  # (1)!
                vm.Container(
                    title="Container I",
                    layout=vm.Layout(grid=[[0, 1]]),  # (2)!
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

        1. Note that the `Page.layout` argument is not specified here and will therefore defaults to `[[0], [1]]`, meaning the containers will be **vertically stacked** down the page in one column.
        2. **Horizontally stack** the components side-by-side inside this `Container` in one row.

    === "app.yaml"
        ```yaml
        # Still requires a .py to add data to the data manager and parse YAML configuration
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

!!! note

    Note that an almost identical layout can also be achieved using solely the [`Page.layout`](layouts.md) by configuring the `Page.layout` as `vm.Layout(grid = [[0, 1], [2, 2]])`.

## Nested containers
Containers can be nested, providing a hierarchical structure for organizing components.
This nesting capability enables users to create more complex layouts and manage related components at any level of granularity.

To create nested containers, add a `Container` to the `components` argument of another `Container`.

```python title="Example"
vm.Container(
    title="Parent Container",
    components=[
        vm.Container(
            title="Child Container",
            components=[vm.Button()]
        )
    ]
)
```
