# How to use tabs

[`Tabs`][vizro.models.Tabs]  organize and separate groups of related content in a dashboard, letting users switch between different sections or views.
They are essentially a way of putting multiple [`Containers`][vizro.models.Container] in the same screen space, and letting the user switch between them.
`Containers` enable the grouping of page components into sections and subsections. See our [user guide on `Containers`](container.md) for more information.

<figure markdown>
  ![tabs](../../assets/user_guides/components/tabs-info.png){ width="400"}
  <figcaption>Displaying multiple containers in Tabs</figcaption>
</figure>

Both `Tabs` and `Containers` are a more advanced technique for customizing your page layout. If you want to arrange components on a page, we recommend reading our [user guide on `Layout`](layouts.md) first.

This guide shows you how to use tabs to organize your `Containers` into subsections inside the dashboard.

By using [`Tabs`][vizro.models.Tabs], the following applies:

- [`Filters`][vizro.models.Filter] affect all components on all tabs (opened and closed) of the page if not specified otherwise inside `Filter.targets`
- The `title` of the  [`Container`][vizro.models.Container] inserted into `Tabs.tabs` will be displayed as a tab label, and the title will be removed from the `Container`


To add [`Tabs`][vizro.models.Tabs] to your page, do the following:

1. Insert the [`Tabs`][vizro.models.Tabs] into the `components` argument of the [`Page`][vizro.models.Page]
2. Insert your [`Containers`][vizro.models.Container] into the `tabs` argument of the [`Tabs`][vizro.models.Tabs]


!!! example "Tabs"
    === "app.py"
        ```py

        import vizro.models as vm
        import vizro.plotly.express as px
        from vizro import Vizro

        gapminder_2007 = px.data.gapminder().query("year == 2007")

        page = vm.Page(
            title="Tabs",
            components=[
                vm.Tabs(
                    tabs=[
                        vm.Container(
                            title="Tab I",
                            components=[
                                vm.Graph(
                                    figure=px.bar(
                                        gapminder_2007,
                                        title="Graph 1",
                                        x="continent",
                                        y="lifeExp",
                                        color="continent",
                                    ),
                                ),
                                vm.Graph(
                                    figure=px.box(
                                        gapminder_2007,
                                        title="Graph 2",
                                        x="continent",
                                        y="lifeExp",
                                        color="continent",
                                    ),
                                ),
                            ],
                        ),
                        vm.Container(
                            title="Tab II",
                            components=[
                                vm.Graph(
                                    figure=px.scatter(
                                        gapminder_2007,
                                        title="Graph 3",
                                        x="gdpPercap",
                                        y="lifeExp",
                                        size="pop",
                                        color="continent",
                                    ),
                                ),
                            ],
                        ),
                    ],
                ),
            ],
            controls=[vm.Filter(column="continent")],
        )

        dashboard = vm.Dashboard(pages=[page])

        Vizro().build(dashboard).run()
        ```
    === "app.yaml"
        ```yaml
        # Still requires a .py to add data to the data manager and parse YAML configuration
        # See from_yaml example
        pages:
          - components:
              - tabs:
                  - title: Tab I
                    type: container
                    components:
                      - type: graph
                        figure:
                            _target_: bar
                            data_frame: gapminder_2007
                            title: Graph 1
                            x: continent
                            y: lifeExp
                            color: continent
                      - type: graph
                        figure:
                            _target_: box
                            data_frame: gapminder_2007
                            title: Graph 2
                            x: continent
                            y: lifeExp
                            color: continent
                  - title: Tab II
                    type: container
                    components:
                      - type: graph
                        figure:
                            _target_: scatter
                            data_frame: gapminder_2007
                            title: Graph 3
                            x: gdpPercap
                            y: lifeExp
                            size: pop
                            color: continent
              type: tabs
          controls:
              - type: filter
                column: continent
          title: Tabs
        ```
    === "Result"
       [![Tabs]][Tabs]

    [Tabs]: ../../assets/user_guides/components/tabs.png
