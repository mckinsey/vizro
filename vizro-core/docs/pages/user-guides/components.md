# Components

Components are the visual building blocks of a Vizro dashboard page. You add them to the `components` argument of a [`Page`][vizro.models.Page] (or [`Container`][vizro.models.Container]) to display charts and tables, present text, group related content into sections, or expose interactive elements such as buttons.

Vizro ships with [`Graph`][vizro.models.Graph], [`Table`][vizro.models.Table], [`AgGrid`][vizro.models.AgGrid], [`Figure`][vizro.models.Figure], [`Card`][vizro.models.Card], [`Text`][vizro.models.Text], [`Button`][vizro.models.Button], [`Container`][vizro.models.Container], and [`Tabs`][vizro.models.Tabs] components. You can also [extend Vizro with your own components](extensions.md).

## When to use which component

Use this table to pick the right component for a given piece of content. Every component below reacts to [controls](controls.md) unless noted otherwise.

| Component                                     | Choose it when you need to…                                                                | Prefer instead…                                                                                                                                                     |
| --------------------------------------------- | ------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`Graph`](graph.md)                           | Render a Plotly Express chart or a [custom Plotly figure](custom-charts.md).               | [`AgGrid`/`Table`](table.md) for tables; [`Figure`](figure.md) for other reactive Dash components.                                                                  |
| [`AgGrid`](table.md#ag-grid)                  | Display an interactive tabular grid (recommended default for tables).                      | [`Table`](table.md#dash-datatable) if you specifically need a Dash DataTable; [`Graph`](graph.md) for a chart.                                                      |
| [`Table`](table.md#dash-datatable)            | Display a Dash DataTable.                                                                  | [`AgGrid`](table.md#ag-grid) is recommended for most tables.                                                                                                        |
| [`Figure`](figure.md)                         | Wrap any other reactive Dash component (including built-in [KPI cards](figure.md#key-performance-indicator-kpi-cards)). | [`Graph`](graph.md), [`AgGrid`/`Table`](table.md) for the common cases; [custom components](custom-components.md) if the component doesn't need to react to controls. |
| [`Card`](card.md)                             | Show a bordered, attention-drawing Markdown callout or a clickable [navigation tile](card.md#create-a-navigation-card). | [`Text`](text.md) for plain Markdown; a [KPI card figure](figure.md#key-performance-indicator-kpi-cards) for KPI tiles; [`Button`](button.md) to trigger an action. |
| [`Text`](text.md)                             | Show plain Markdown text with no border or background.                                     | [`Card`](card.md) if you want it to stand out.                                                                                                                      |
| [`Button`](button.md)                         | Let users trigger an [action](actions.md), submit a form, or navigate to a URL.            | [`Filter`](filters.md) / [`Parameter`](parameters.md) for control-like behavior; [`Card`'s navigation tile](card.md#create-a-navigation-card) for click-to-navigate. |
| [`Container`](container.md)                   | Group components into a nested section with its own layout, styling, or scoped controls.   | [`Page.layout`](layouts.md) alone for simple arrangements; [`Tabs`](tabs.md) to switch between multiple containers.                                                 |
| [`Tabs`](tabs.md)                             | Let users switch between multiple [`Container`s](container.md) that share the same space.  | A single [`Container`](container.md) if all content should be visible at once.                                                                                      |

<div class="grid cards" markdown>

- :octicons-graph-16:{ .lg .middle } __Graph__

    ---

    Visualize data with any Plotly chart.

    [:octicons-arrow-right-24: View user guide](graph.md)

- :material-table-large:{ .lg .middle } __Table__

    ---

    Visualize tabular data.

    [:octicons-arrow-right-24: View user guide](table.md)

- :material-graph:{ .lg .middle } __Figure__

    ---

    Make any [Dash component](https://dash.plotly.com/#open-source-component-libraries) reactive.

    [:octicons-arrow-right-24: View user guide](figure.md)

- :material-cards-outline:{ .lg .middle } __Card__

    ---

    Call out text or display KPIs.

    [:octicons-arrow-right-24: View user guide](card.md)

- :material-play-box-outline:{ .lg .middle } __Button__

    ---

    Navigate to different URLs or trigger an [action](actions.md).

    [:octicons-arrow-right-24: View user guide](button.md)

- :material-language-markdown:{ .lg .middle } __Text__

    ---

    Display plain text, add images, links and more.

    [:octicons-arrow-right-24: View user guide](text.md)

- :octicons-table-16:{ .lg .middle } __Container__

    ---

    Group components into sections and subsections.

    [:octicons-arrow-right-24: View user guide](container.md)

- :material-tab-plus:{ .lg .middle } __Tab__

    ---

    Group containers and navigate between them.

    [:octicons-arrow-right-24: View user guide](tabs.md)

</div>
