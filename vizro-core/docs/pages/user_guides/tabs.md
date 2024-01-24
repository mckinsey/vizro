# How to use tabs

Tabs organize and separate groups of related content in a dashboard, letting users navigate between different sections or views within a click.
This guide shows you how to use tabs to organize your containers into subsections inside the dashboard.

To add [`Tabs`][vizro.models.Tabs] to your page, do the following:

1. Insert the [`Tabs`][vizro.models.Tabs] into the `components` argument of the [`Page`][vizro.models.Page]
2. Insert your [`Containers`][vizro.models.Container] into the `components` argument of the [`Tabs`][vizro.models.Tabs]

By using the [`Tabs`][vizro.models.Tabs], the following applies:
- [`Filters`][vizro.models.Filter] affect all components on all tabs (opened and closed) of the page if not specified otherwise inside `Filter.targets`
- The `title` of the outer [`Container`][vizro.models.Container] inserted into `Tabs.components` will be displayed as a tab label, and the title will removed from the `Container`
- If you want to keep the `Container.title` inside the Tab, you can apply custom CSS
- If you want a different `Container.title` inside the tab, add a nested [`Container`][vizro.models.Container]


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
        # Still requires a .py to register data connector in Data Manager and parse yaml configuration
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
