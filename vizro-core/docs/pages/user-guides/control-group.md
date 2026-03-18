# How to use control groups

This guide shows you how to use control groups to organize [controls](controls.md) on a page. A [ControlGroup][vizro.models.ControlGroup] is a container that groups together [filters](filters.md) and [parameters](parameters.md) under a title. It helps you structure the control panel on the left side of a [page](pages.md) into logical sections.

Control groups are only available for page level controls.

## When to use control groups

Use a control group when you want to:

- Visually separate different sets of controls on the same page (for example, "Filters" and "Parameters").
- Add a title or short description to a subset of controls so users understand what they affect.
- Keep the page control panel organized when you have many controls.

!!! example "Control Group"

    === "app.py"

        ```{.python pycafe-link hl_lines="12-14"}
        from vizro import Vizro
        import vizro.plotly.express as px
        import vizro.models as vm

        iris = px.data.iris()

        page = vm.Page(
            title="My first page",
            components=[
                vm.Graph(
                    id="scatter-chart",
                    figure=px.scatter(iris, x="sepal_length", y="petal_width", color="species")
                ),
            ],
            controls=[
                vm.ControlGroup(
                    title="Filters",
                    controls=[
                        vm.Filter(column="species"),
                        vm.Filter(column="sepal_length")
                    ]
                ),
                vm.ControlGroup(
                    title="Parameter",
                    controls=[
                        vm.Parameter(
                            targets=["scatter_chart.title"],
                            selector=vm.Dropdown(
                                options=["My scatter chart", "A better title!", "Another title..."],
                                multi=False,
                            ),
                        ),
                    ]
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
          - title: My first page
            components:
              - id: scatter-chart
                figure:
                  _target_: scatter
                  data_frame: iris
                  x: sepal_length
                  y: petal_width
                  color: species
                type: graph
            controls:
              - type: control_group
                title: Filters
                controls:
                  - column: species
                    type: filter
                  - column: sepal_length
                    type: filter
              - type: control_group
                title: Parameter
                controls:
                  - type: parameter
                    targets:
                      - scatter-chart.title
                    selector:
                      options: [My scatter chart", A better title!, Another title...]
                      multi: false
                      type: dropdown
        ```

    === "Result"

        \[![Filter]\][filter]
