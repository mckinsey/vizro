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

## Group controls

To organize the control panel on a page into sections, you can group [filters](filters.md) and [parameters](parameters.md) under a title using a [`ControlGroup`][vizro.models.ControlGroup]. Control groups are only available for page-level controls. Use a control group when you want to:

- Visually separate different sets of controls on the same page (for example, "Filters" and "Parameters").
- Add a title or short description to a subset of controls so users understand what they affect.
- Keep the page control panel organized when you have many controls.

!!! example "Control Group"

    === "app.py"

        ```{.python pycafe-link hl_lines="16-22"}
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

## Sync controls

You can keep two controls in sync so that changing one automatically applies the same value to the other. This is useful, for example, when you need to both filter and parametrize a chart from the same user selection, such as filtering a chart down to one species and also using that species to set the chart's title. The two controls can be on the same page or on [different pages](#sync-controls-across-pages).

To sync controls, add another control's `id` to the `targets` of a [filter](filters.md) or [parameter](parameters.md). Whenever the control changes, Vizro sets the targeted control to the same value (using the [`set_control` action][vizro.actions.set_control] behind the scenes) and then refreshes both controls' figure targets. All combinations work: filter and filter, parameter and parameter, and filter and parameter.

!!! note "A parameter always needs a figure target"

    A [filter](filters.md) that targets only other controls still applies to the page's figures: it falls back to every figure whose data includes its `column`, exactly as if no `targets` were given. A [parameter](parameters.md) has no such fallback, because it applies its value through its `<component>.<argument>` targets. A parameter must therefore always target at least one figure argument in addition to any controls it syncs.

!!! note "A control that only drives other controls is not a Filter or Parameter"

    By design a [filter](filters.md) and [parameter](parameters.md) always act on figures, so above mean neither can exist purely to drive other controls. A filter with no figure target *is not a filter*, and a parameter with no figure target *is not a parameter*.

    If a control that only sets other controls (and filters or parametrizes nothing itself) is exactly what you want, skip the filter/parameter wrapper: put a bare [selector](selectors.md) (for example a [`RadioItems`][vizro.models.RadioItems]) straight into the layout and give it an explicit [`set_control`][vizro.actions.set_control] action for each control it should drive. The targeted controls do the actual figure work when their value changes. A selector is normally only allowed inside a filter or parameter, so first whitelist it on its parent with the [`add_type`][vizro.models.VizroBaseModel.add_type] like:

    ```python
    import vizro.models as vm
    from vizro.actions import set_control

    vm.Page.add_type("components", vm.RadioItems)  # allow a bare selector as a component (Container.add_type also works)

    # ...then, as a Page component:
    vm.RadioItems(
        options=["setosa", "versicolor", "virginica"],
        actions=[set_control(control="species_filter_1", value=None), set_control(control="species_filter_2", value=None)],
    )
    ```

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
            title=f"Species: {selected_species}"  # (1)!
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

        1. The [custom chart](custom-charts.md) turns the raw `selected_species` value into a human-readable title (for example `"setosa"` becomes _"Species: setosa"_). Because the title is built inside the figure function, the parameter can drive any derived output, not just a literal string.
        1. The filter targets its own graph as usual, plus `title_parameter`. Changing the filter filters the chart and sets `title_parameter` to the same species.
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

### Sync controls across pages

A control's `targets` can also list controls on **other pages**. This lets you build **global controls**: a single control on one page that drives figures on many pages. Point a control on your main page at a control on each of the other pages, then hide those other controls with `visible=False`. The user only ever interacts with the control on the main page, but every page stays filtered and parametrized by the same value.

Cross-page syncing works exactly like same-page syncing — you still just add the target control's `id` to `targets` — with one behavioral difference: a value set on one page is applied to the synced control on another page **when you open that page**, rather than instantly. Vizro keeps the value in an internal browser-session store, so it also survives a full page refresh within the session.

!!! example "Global controls across three pages"

    === "app.py"

        ```{.python pycafe-link hl_lines="7 20 25 41"}
        import vizro.models as vm
        import vizro.plotly.express as px
        from vizro import Vizro
        from vizro.managers import data_manager


        def load_iris(sample_size=100):  # (1)!
            return px.data.iris().sample(sample_size, random_state=42)


        data_manager["iris"] = load_iris

        overview_page = vm.Page(
            title="Overview",
            components=[
                vm.Graph(id="overview_graph", figure=px.scatter("iris", x="sepal_width", y="sepal_length", color="species")),
            ],
            controls=[
                vm.Parameter(
                    targets=["overview_graph.data_frame.sample_size", "detail_sample_size", "summary_sample_size"],  # (2)!
                    selector=vm.Slider(min=50, max=150, step=25, value=100, title="Sample size"),
                ),
                vm.Filter(
                    column="species",
                    targets=["overview_graph", "detail_species", "summary_species"],  # (3)!
                    selector=vm.Dropdown(title="Species"),
                ),
            ],
        )

        detail_page = vm.Page(
            title="Detail",
            components=[
                vm.Graph(id="detail_graph", figure=px.scatter("iris", x="petal_width", y="petal_length", color="species")),
            ],
            controls=[
                vm.Parameter(
                    id="detail_sample_size",
                    targets=["detail_graph.data_frame.sample_size"],
                    selector=vm.Slider(min=50, max=150, step=25, value=100),
                    visible=False,  # (4)!
                ),
                vm.Filter(id="detail_species", column="species", targets=["detail_graph"], visible=False),
            ],
        )

        summary_page = vm.Page(
            title="Summary",
            components=[
                vm.Graph(id="summary_graph", figure=px.box("iris", x="species", y="sepal_length", color="species")),
            ],
            controls=[
                vm.Parameter(
                    id="summary_sample_size",
                    targets=["summary_graph.data_frame.sample_size"],
                    selector=vm.Slider(min=50, max=150, step=25, value=100),
                    visible=False,
                ),
                vm.Filter(id="summary_species", column="species", targets=["summary_graph"], visible=False),
            ],
        )

        dashboard = vm.Dashboard(pages=[overview_page, detail_page, summary_page])
        Vizro().build(dashboard).run()
        ```

        1. A [dynamic data](data.md#dynamic-data) loader whose `sample_size` argument controls how many rows are loaded. A [parameter can drive this argument](parameters.md#dynamic-data-parameters) via a `data_frame.sample_size` target.
        1. The parameter targets its own graph's `data_frame.sample_size` **and** the hidden `sample_size` parameters on the other two pages, so the sample size stays in sync everywhere.
        1. The filter targets its own graph **and** the hidden `species` filters on the other two pages.
        1. `visible=False` hides the control on _Detail_ and _Summary_. The user never sees it, but it still filters and parametrizes that page's figure using the value synced from _Overview_.

    === "app.yaml"

        ```yaml
        # Still requires a .py to register the dynamic data source "iris" and parse YAML configuration
        # See yaml_version example
        pages:
          - title: Overview
            components:
              - id: overview_graph
                type: graph
                figure:
                  _target_: scatter
                  data_frame: iris
                  x: sepal_width
                  y: sepal_length
                  color: species
            controls:
              - type: parameter
                targets: [overview_graph.data_frame.sample_size, detail_sample_size, summary_sample_size]
                selector:
                  type: slider
                  min: 50
                  max: 150
                  step: 25
                  value: 100
                  title: Sample size
              - type: filter
                column: species
                targets: [overview_graph, detail_species, summary_species]
                selector:
                  type: dropdown
                  title: Species
          - title: Detail
            components:
              - id: detail_graph
                type: graph
                figure:
                  _target_: scatter
                  data_frame: iris
                  x: petal_width
                  y: petal_length
                  color: species
            controls:
              - id: detail_sample_size
                type: parameter
                targets: [detail_graph.data_frame.sample_size]
                visible: false
                selector:
                  type: slider
                  min: 50
                  max: 150
                  step: 25
                  value: 100
              - id: detail_species
                type: filter
                column: species
                targets: [detail_graph]
                visible: false
          - title: Summary
            components:
              - id: summary_graph
                type: graph
                figure:
                  _target_: box
                  data_frame: iris
                  x: species
                  y: sepal_length
                  color: species
            controls:
              - id: summary_sample_size
                type: parameter
                targets: [summary_graph.data_frame.sample_size]
                visible: false
                selector:
                  type: slider
                  min: 50
                  max: 150
                  step: 25
                  value: 100
              - id: summary_species
                type: filter
                column: species
                targets: [summary_graph]
                visible: false
        ```

The same mechanism powers **drill-through**: when a `set_control` is triggered from a figure or component (a [`Graph`][vizro.models.Graph], [`AgGrid`][vizro.models.AgGrid], [`Button`][vizro.models.Button], or [`Card`][vizro.models.Card]) rather than from a control's own selector, and its target control is on another page, Vizro navigates to that page and applies the value there. See [graph and table interactions](graph-table-actions.md) for more.

!!! note "Things to know about cross-page syncing"

    - **Values apply on page open, not live.** Changing a control updates its cross-page targets the next time you open their pages, not while you are still on the source page.
    - **Syncing is not transitive.** If page A syncs to page B and page B syncs to page C, opening page B restores its value from A but does not itself re-trigger the B → C sync. C only updates when you actually change B's control. To keep all three in sync, target them directly from A instead, for example `targets=["B_control", "C_control"]`.
    - **Reset is per page.** The "Reset controls" button resets only the current page. A synced control can therefore temporarily differ from its source after a reset, until you change the source again.
    - **Keep synced controls compatible.** Vizro applies the value as-is and does not validate that the two controls accept the same kind of value. Syncing, say, a species selection into a numeric range would coerce the value and can filter to nothing. If a synced control is a [dynamic filter](data.md#filters), make sure the synced value is still a valid option after the data refreshes.

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

[controlgroup]: ../../assets/user_guides/control/control_group.png
[applycontrolswithabutton]: ../../assets/user_guides/control/apply_controls_with_a_button.gif
[synccontrols]: ../../assets/user_guides/control/sync_controls.gif
