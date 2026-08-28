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

## Sync controls

You can keep two controls in sync so that changing one automatically applies the same value to the other. This is useful, for example, when you need to both filter and parametrize a chart from the same user selection, such as filtering a chart down to one species and also using that species to set the chart's title.

To sync controls, add another control's `id` to the `targets` of a [filter](filters.md) or [parameter](parameters.md). Whenever the control changes, Vizro sets the targeted control to the same value (using the [`set_control` action][vizro.actions.set_control] behind the scenes) and then refreshes that control's own targets. All combinations work: filter and filter, parameter and parameter, and filter and parameter, and any [selector](selectors.md) can be used, so the two controls do not even need to share the same selector type.

!!! note "Controls can only sync on the same page (for now)"

    A control can currently only target another control on the **same page**. Support for syncing controls **across pages** is coming soon, at which point this limitation is removed.

!!! note "A parameter always needs a figure target"

    A [filter](filters.md) that targets only other controls still applies to the page's figures: it falls back to every figure whose data includes its `column`, exactly as if no `targets` were given. A [parameter](parameters.md) has no such fallback, because it applies its value through its `<component>.<argument>` targets. A parameter must therefore always target at least one figure argument in addition to any controls it syncs.

!!! example "Sync a filter with a hidden parameter"

    === "app.py"

        ```{.python pycafe-link hl_lines="11 22 25"}
        import vizro.models as vm
        import vizro.plotly.express as px
        from vizro import Vizro
        from vizro.models.types import capture

        iris = px.data.iris()


        @capture("graph")
        def scatter_with_title(data_frame, selected_species):
            title=f"Sepal length vs. width for species: {selected_species}"  # (1)!             
            fig = px.scatter(data_frame, x="sepal_length", y="sepal_width", color="species", title=title) 
            return fig


        page = vm.Page(
            title="Sync controls",
            components=[
                vm.Graph(id="scatter_chart", figure=scatter_with_title(data_frame=iris, selected_species="setosa")),
            ],
            controls=[
                vm.Filter(column="species", targets=["scatter_chart", "title_parameter"], selector=vm.RadioItems()),  # (2)!
                vm.Parameter(
                    id="title_parameter",
                    targets=["scatter_chart.selected_species"],  # (3)!
                    selector=vm.RadioItems(options=["setosa", "versicolor", "virginica"], value="setosa"),
                    visible=False,
                ),
            ],
        )

        dashboard = vm.Dashboard(pages=[page])
        Vizro().build(dashboard).run()
        ```

        1. The [custom chart](custom-charts.md) turns the raw `selected_species` value into a human-readable title (for example `"setosa"` becomes _"Sepal length vs. width — Iris setosa"_). Because the title is built inside the figure function, the parameter can drive any derived output, not just a literal string.
        1. The filter targets its own graph as usual, plus `title_parameter`. Changing the filter filters the chart and sets `title_parameter` to the same species. The filter uses a single-select [`RadioItems`][vizro.models.RadioItems] selector so its value maps one-to-one onto the single-select parameter it syncs.
        1. `title_parameter` feeds the selected species into the custom chart's `selected_species` argument, which composes the title from it. Its selector is hidden with `visible=False` because the user only interacts with the filter; the parameter's value is driven entirely by the sync.

    === "app.yaml"

        ```yaml
        # Still requires a .py to add data to the data manager, define CapturedCallables, and parse YAML configuration
        # See yaml_version example
        pages:
          - title: Sync controls
            components:
              - id: scatter_chart
                type: graph
                figure:
                  _target_: __main__.scatter_with_title
                  data_frame: iris
                  selected_species: setosa
            controls:
              - type: filter
                column: species
                targets: [scatter_chart, title_parameter]
                selector:
                  type: radio_items
              - id: title_parameter
                type: parameter
                targets: [scatter_chart.selected_species]
                selector:
                  type: radio_items
                  options: [setosa, versicolor, virginica]
                  value: setosa
                visible: false
        ```

    === "Result"

        [![SyncControls]][synccontrols]

You can combine syncing with [applying controls on a button click](#apply-controls-with-a-button): give a control's selector an explicit [`set_control`][vizro.actions.set_control] action to sync its partner without refreshing figures on change, then refresh the figures together with an [`update_targets`][vizro.actions.update_targets] button.

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
[synccontrols]: ../../assets/user_guides/control/sync_controls.gif
