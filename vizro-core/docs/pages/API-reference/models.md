# Models

Vizro's grammar of dashboards is defined by a small set of Pydantic models in `vizro.models`, typically aliased as `vm` (`import vizro.models as vm`). Every dashboard is built by composing these models. Use the [Model index](#model-index) below to jump to the reference entry for a specific model; the full auto-generated reference for every public model follows in the [full model reference](#full-model-reference) section.

## Model index

### Dashboard structure

| Model                                     | Purpose                                                                                                                                                                                    |
| ----------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`Dashboard`][vizro.models.Dashboard]     | Top-level model. Combines pages, navigation, theme, and dashboard-level metadata. See the [dashboard user guide](../user-guides/dashboard.md).                                              |
| [`Page`][vizro.models.Page]               | A single page. Holds `components`, `controls`, `layout`, and optional `path`/`id`. See the [pages user guide](../user-guides/pages.md).                                                     |
| [`Container`][vizro.models.Container]     | Groups components into a nested section with its own layout, styling, or scoped controls. See the [container user guide](../user-guides/container.md).                                      |
| [`Tabs`][vizro.models.Tabs]               | Displays multiple `Container`s in the same screen space with tab labels. See the [tabs user guide](../user-guides/tabs.md).                                                                 |

### Layouts

| Model                          | Purpose                                                                                                                                          |
| ------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| [`Grid`][vizro.models.Grid]    | Default row/column grid layout. See the [layouts user guide](../user-guides/layouts.md#grid-layout).                                             |
| [`Flex`][vizro.models.Flex]    | Flexible-box layout for responsive arrangements. See the [layouts user guide](../user-guides/layouts.md#flex-layout).                            |
| [`Layout`][vizro.models.Layout] | Deprecated alias for `Grid`. See the [deprecations page](deprecations.md). Prefer `Grid` in new code.                                             |

### Visualization components

| Model                              | Purpose                                                                                                                                       |
| ---------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| [`Graph`][vizro.models.Graph]      | Renders a Plotly Express chart or a [custom Plotly figure](../user-guides/custom-charts.md). See the [graph user guide](../user-guides/graph.md). |
| [`Table`][vizro.models.Table]      | Renders a Dash DataTable. See the [table user guide](../user-guides/table.md#dash-datatable).                                                 |
| [`AgGrid`][vizro.models.AgGrid]    | Renders a Dash AG Grid (recommended default for tabular data). See the [table user guide](../user-guides/table.md#ag-grid).                    |
| [`Figure`][vizro.models.Figure]    | Renders any reactive Dash component (including [KPI card figures](../user-guides/figure.md#key-performance-indicator-kpi-cards)).             |

### Text and interactive components

| Model                            | Purpose                                                                                                                                                              |
| -------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`Card`][vizro.models.Card]      | Bordered Markdown callout or clickable navigation tile. See the [card user guide](../user-guides/card.md).                                                           |
| [`Text`][vizro.models.Text]      | Plain, unstyled Markdown text. See the [text user guide](../user-guides/text.md).                                                                                    |
| [`Button`][vizro.models.Button]  | Triggers an [action](../user-guides/actions.md), submits a form, or navigates. See the [button user guide](../user-guides/button.md).                                |
| [`Tooltip`][vizro.models.Tooltip] | Inline icon that reveals contextual Markdown help on hover. Passed to a component's `description` argument.                                                          |

### Controls

| Model                                     | Purpose                                                                                                                                                    |
| ----------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`Filter`][vizro.models.Filter]           | Applies a filter to one or more components based on a column value. See the [filters user guide](../user-guides/filters.md).                               |
| [`Parameter`][vizro.models.Parameter]     | Overrides a function argument on one or more components. See the [parameters user guide](../user-guides/parameters.md).                                    |
| [`ControlGroup`][vizro.models.ControlGroup] | Groups related controls together in the sidebar for organization.                                                                                          |

### Selectors

Selectors are the input widgets used inside `Filter.selector` and `Parameter.selector`. Vizro auto-selects a selector based on column dtype; see [selectors user guide](../user-guides/selectors.md) for details.

| Model                                   | Purpose                                                                              |
| --------------------------------------- | ------------------------------------------------------------------------------------ |
| [`Dropdown`][vizro.models.Dropdown]     | Single- or multi-select dropdown (default for categorical data).                     |
| [`Checklist`][vizro.models.Checklist]   | Multi-select checkbox group.                                                         |
| [`RadioItems`][vizro.models.RadioItems] | Single-select radio-button group.                                                    |
| [`Switch`][vizro.models.Switch]         | Boolean toggle (default for boolean data).                                           |
| [`Slider`][vizro.models.Slider]         | Single numeric slider.                                                               |
| [`RangeSlider`][vizro.models.RangeSlider] | Numeric range slider (default for numerical data).                                   |
| [`DatePicker`][vizro.models.DatePicker] | Date or date-range picker (default for temporal data).                               |
| [`TimePicker`][vizro.models.TimePicker] | Time or time-range picker.                                                           |
| [`DateTimePicker`][vizro.models.DateTimePicker] | Combined date-and-time (or date-and-time-range) picker for `datetime` columns.       |
| [`Cascader`][vizro.models.Cascader]     | Cascading multi-level selection widget.                                              |

### Navigation

| Model                                | Purpose                                                                                            |
| ------------------------------------ | -------------------------------------------------------------------------------------------------- |
| [`Navigation`][vizro.models.Navigation] | Top-level navigation model for the dashboard. See the [navigation user guide](../user-guides/navigation.md). |
| [`NavBar`][vizro.models.NavBar]      | Icon-style sidebar or horizontal navigation bar composed of `NavLink`s.                            |
| [`NavLink`][vizro.models.NavLink]    | A single icon-linked entry in a `NavBar`, optionally containing an `Accordion` of pages.           |
| [`Accordion`][vizro.models.Accordion] | Grouped, collapsible page list used for the default sidebar navigation.                            |

### Actions

| Model                            | Purpose                                                                                                            |
| -------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| [`Action`][vizro.models.Action]  | Wraps a custom action function or a built-in action (see [`vizro.actions`](actions.md)) with `function`, `inputs`, and `outputs`. |

### Base and typing

| Model                                                | Purpose                                                                                                       |
| ---------------------------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| [`VizroBaseModel`][vizro.models.VizroBaseModel]      | Base class for every Vizro model. Extend it when [writing a custom component](../user-guides/custom-components.md). |
| [`capture`][vizro.models.types.capture]              | Decorator used to register a custom chart, table, figure, or action. See [`vizro.models.types`](#full-model-reference). |
| [`CapturedCallable`][vizro.models.types.CapturedCallable] | Wrapper produced by `@capture(...)` that carries the callable plus captured arguments through the model layer.       |

## Full model reference

The auto-generated reference below covers every public model in `vizro.models` and `vizro.models.types`. Anchors used by the [Model index](#model-index) above resolve into this section.

<!-- vale off -->

::: vizro.models
    options:
      filters: ["!^_","!build","!model_post_init"] # Don't show underscore methods, build method, and model_post_init

::: vizro.models.types
    options:
      filters: ["!^_"]  # Don't show dunder methods as well as single underscore ones
      merge_init_into_class: false

<!-- vale on -->
