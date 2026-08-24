---
description: "Cross-cutting control patterns: set a control's value programmatically via `set_control`, reset controls to defaults, and group controls in the panel."
---

# Controls

Vizro supports _controls_ to perform common business intelligence (BI) operations. This guide gives an overview of the different ways you can configure controls.

The following [components](components.md) are reactive to controls:

- [built-in graphs](graph.md) and [custom graphs](custom-charts.md)
- [built-in tables](table.md) and [custom tables](custom-tables.md)
- [built-in figures](figure.md) and [custom figures](custom-figures.md)

It is possible to add controls to a [page](pages.md) or [container](container.md#add-controls-to-container). Both the [`Page` model][vizro.models.Page] and the [`Container` model][vizro.models.Container] have an optional `controls` argument where you can configure any number of controls.

Vizro has two types of control:

- [Filter](filters.md) controls the [data](data.md) of reactive components. It filters the `data_frame` of the `figure` function of a target component model such as [`Graph`][vizro.models.Graph].

- [Parameter](parameters.md) controls the configuration of a reactive component. It sets any argument other than `data_frame` in the `figure` function of the target component model such as [`Graph`][vizro.models.Graph]. It can also be used to set [dynamic data parameters](parameters.md#dynamic-data-parameters).

All controls have an [argument `selector`](selectors.md) that configures the visual interface for the control, for example a checklist or a range slider. The same selectors are available for all controls.

## Set a control

When the dashboard is running there are two ways for a user to set a control:

- Direct user interaction with the underlying selector. For example, the user selects values from a checklist.
- [User interaction with a graph or table](graph-table-actions.md) via the [`set_control` action][vizro.actions.set_control]. This enables functionality such as [cross-filtering](graph-table-actions.md#cross-filter) and [cross-highlighting](graph-table-actions.md#cross-highlight). To achieve a visually cleaner dashboard you might like to hide the control's underlying selector by setting the control's argument `visible=False`.

!!! tip

    The state of any control that has [`show_in_url=True`](run-deploy.md#shareable-url) is included when you share the URL of your app.

## Reset controls

You can reset all controls on the page to their original values with the "Reset controls" button at the bottom of the control panel on the left side of the page. This applies to all controls on the page, regardless of whether they are visible. When all controls on a page have `visible=False` and hence no control panel is shown, the "Reset controls" button appears next to the theme switch on the top right of the page.

## Apply controls with a button

By default, changing a control immediately refreshes the components it targets. Sometimes you would rather let a user adjust several controls first and apply them all at once, for example to avoid recomputing an expensive figure on every change.

To stop a control from refreshing its targets as soon as its value changes, set its [`selector`](selectors.md)'s `actions=None`. The control still contributes its value whenever its targets are refreshed by something else; it just no longer triggers a refresh on its own.

To refresh the targets on demand, add a [`Button`][vizro.models.Button] that runs the [`update_targets`][vizro.actions.update_targets] action. A bare `va.update_targets()` refreshes every figure on the page (and recomputes the options of any [dynamic filters](data.md#filters)); pass `targets` to refresh only specific components. See the [actions guide](actions.md#refresh-figures-on-demand) for more on `update_targets`.

!!! example "Apply controls with a button"

    === "app.py"

        ```{.python pycafe-link hl_lines="15 18 21"}
        import vizro.actions as va
        import vizro.models as vm
        import vizro.plotly.express as px
        from vizro import Vizro

        iris = px.data.iris()

        page = vm.Page(
            title="Apply controls with a button",
            components=[
                vm.Graph(
                    id="scatter_chart",
                    figure=px.scatter(iris, x="sepal_length", y="petal_width", color="species"),
                ),
                vm.Button(text="Apply controls", actions=va.update_targets()),  # (1)!
            ],
            controls=[
                vm.Filter(column="species", selector=vm.Checklist(actions=None)),  # (2)!
                vm.Parameter(
                    targets=["scatter_chart.x"],
                    selector=vm.RadioItems(options=["sepal_length", "petal_length"], actions=None),  # (3)!
                ),
            ],
        )

        dashboard = vm.Dashboard(pages=[page])
        Vizro().build(dashboard).run()
        ```

        1. The [`update_targets`][vizro.actions.update_targets] action refreshes the page's figures using the current control values. Called with no arguments it refreshes every figure on the page; pass `targets` to refresh only specific components.
        1. Setting the selector's `actions=None` stops the filter from applying as soon as its value changes. Its value is still used whenever the graph is refreshed, here when the button is clicked.
        1. Setting the selector's `actions=None` stops the parameter from applying as soon as its value changes. Its value is still used whenever the graph is refreshed, here when the button is clicked.

    === "app.yaml"

        ```yaml
        # Still requires a .py to add data to the data manager and parse YAML configuration
        # See yaml_version example
        pages:
          - title: Apply controls with a button
            components:
              - id: scatter_chart
                figure:
                  _target_: scatter
                  data_frame: iris
                  x: sepal_length
                  y: petal_width
                  color: species
                type: graph
              - type: button
                text: Apply controls
                actions:
                  - type: update_targets
            controls:
              - column: species
                type: filter
                selector:
                  type: checklist
                  actions: []
              - type: parameter
                targets:
                  - scatter_chart.x
                selector:
                  type: radio_items
                  options: [sepal_length, petal_length]
                  actions: null
        ```

    === "Result"

        [![ApplyControlsWithAButton]][applycontrolswithabutton]

## Group controls

To organize the control panel on a page into sections, you can group [filters](filters.md) and [parameters](parameters.md) under a title using a [`ControlGroup`][vizro.models.ControlGroup]. Control groups are only available for page-level controls. Use a control group when you want to:

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
                    id="scatter_chart",
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
              - id: scatter_chart
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
                      options: [My scatter chart, A better title!, Another title...]
                      multi: false
                      type: dropdown
        ```

    === "Result"

        [![ControlGroup]][controlgroup]

[controlgroup]: ../../assets/user_guides/control/control_group.png
[applycontrolswithabutton]: ../../assets/user_guides/control/apply_controls_with_a_button.gif
