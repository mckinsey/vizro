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

When the dashboard is running there are two ways for a user to set a control:

- Direct user interaction with the underlying selector. For example, the user selects values from a checklist.
- [User interaction with a graph or table](graph-table-actions.md) via the [`set_control` action][vizro.actions.set_control]. This enables functionality such as [cross-filtering](graph-table-actions.md#cross-filter) and [cross-highlighting](graph-table-actions.md#cross-highlight).

!!! tip

    The state of any control that has [`show_in_url=True`](run-deploy.md#shareable-url) is included when you share the URL of your app.
