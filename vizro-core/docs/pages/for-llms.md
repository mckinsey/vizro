# Vizro for LLMs

This page is a single-file cheatsheet for LLMs and coding agents. It restates only what an agent needs to write correct Vizro code in one pass, and links out to canonical reference for everything else. Do not duplicate content from linked pages here — follow the links.

## Minimum runnable app

Five lines of Python produce a running Vizro dashboard:

```python
import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro

Vizro().build(vm.Dashboard(pages=[vm.Page(title="Iris", components=[vm.Graph(figure=px.scatter(px.data.iris(), x="sepal_length", y="sepal_width", color="species"))])])).run()
```

Longer walk-through: [quickstart tutorial](tutorials/quickstart-tutorial.md).

## Model index (`vizro.models`, alias `vm`)

Every dashboard is a tree of these models. See the full [model reference](API-reference/models.md) for API docs; the user-guide link explains when to reach for each one.

| Model                                     | One-liner                                                                                          | Guide                                                    |
| ----------------------------------------- | -------------------------------------------------------------------------------------------------- | -------------------------------------------------------- |
| [`Dashboard`][vizro.models.Dashboard]     | Top-level model. Combines pages, navigation and theme.                                             | [Dashboard](user-guides/dashboard.md)                    |
| [`Page`][vizro.models.Page]               | A single page. Holds `components`, `controls`, `layout`.                                           | [Page](user-guides/pages.md)                             |
| [`Container`][vizro.models.Container]     | Nested section with its own layout, style, or scoped controls.                                     | [Container](user-guides/container.md)                    |
| [`Tabs`][vizro.models.Tabs]               | Switch between several `Container`s sharing screen space.                                          | [Tabs](user-guides/tabs.md)                              |
| [`Grid`][vizro.models.Grid]               | Default row/column grid layout.                                                                    | [Layouts](user-guides/layouts.md#grid-layout)            |
| [`Flex`][vizro.models.Flex]               | Flexible-box layout.                                                                               | [Layouts](user-guides/layouts.md#flex-layout)            |
| [`Layout`][vizro.models.Layout]           | Deprecated alias for `Grid`. Prefer `Grid` in new code.                                            | [Deprecations](API-reference/deprecations.md)            |
| [`Graph`][vizro.models.Graph]             | Plotly Express or custom Plotly chart.                                                             | [Graph](user-guides/graph.md)                            |
| [`AgGrid`][vizro.models.AgGrid]           | Dash AG Grid (recommended for tables).                                                             | [Table](user-guides/table.md#ag-grid)                    |
| [`Table`][vizro.models.Table]             | Dash DataTable.                                                                                    | [Table](user-guides/table.md#dash-datatable)             |
| [`Figure`][vizro.models.Figure]           | Any reactive Dash component (includes built-in KPI cards).                                         | [Figure](user-guides/figure.md)                          |
| [`Card`][vizro.models.Card]               | Bordered Markdown callout or navigation tile.                                                      | [Card](user-guides/card.md)                              |
| [`Text`][vizro.models.Text]               | Plain, unstyled Markdown text.                                                                     | [Text](user-guides/text.md)                              |
| [`Button`][vizro.models.Button]           | Trigger an action, submit a form, or navigate.                                                     | [Button](user-guides/button.md)                          |
| [`Tooltip`][vizro.models.Tooltip]         | Icon that reveals contextual Markdown help; used as a component's `description`.                   | (See per-component `description` in user guides.)         |
| [`Filter`][vizro.models.Filter]           | Filter that targets one or more components on a column value.                                      | [Filters](user-guides/filters.md)                        |
| [`Parameter`][vizro.models.Parameter]     | Override a function argument on target components.                                                 | [Parameters](user-guides/parameters.md)                  |
| [`ControlGroup`][vizro.models.ControlGroup] | Group related controls in the sidebar.                                                             | [Controls](user-guides/controls.md#group-controls)       |
| [`Dropdown`][vizro.models.Dropdown]       | Single/multi-select dropdown selector.                                                             | [Selectors](user-guides/selectors.md)                    |
| [`Checklist`][vizro.models.Checklist]     | Multi-select checkbox group selector.                                                              | [Selectors](user-guides/selectors.md)                    |
| [`RadioItems`][vizro.models.RadioItems]   | Single-select radio button selector.                                                               | [Selectors](user-guides/selectors.md)                    |
| [`Switch`][vizro.models.Switch]           | Boolean toggle selector.                                                                           | [Selectors](user-guides/selectors.md)                    |
| [`Slider`][vizro.models.Slider]           | Single numeric slider.                                                                             | [Selectors](user-guides/selectors.md)                    |
| [`RangeSlider`][vizro.models.RangeSlider] | Numeric range slider.                                                                              | [Selectors](user-guides/selectors.md)                    |
| [`DatePicker`][vizro.models.DatePicker]   | Date / date-range picker.                                                                          | [Selectors](user-guides/selectors.md)                    |
| [`TimePicker`][vizro.models.TimePicker]   | Time / time-range picker.                                                                          | [Selectors](user-guides/selectors.md)                    |
| [`Cascader`][vizro.models.Cascader]       | Cascading multi-level selector.                                                                    | [Selectors](user-guides/selectors.md)                    |
| [`Navigation`][vizro.models.Navigation]   | Dashboard navigation model.                                                                        | [Navigation](user-guides/navigation.md)                  |
| [`NavBar`][vizro.models.NavBar]           | Icon sidebar or horizontal bar of `NavLink`s.                                                      | [Navigation](user-guides/navigation.md)                  |
| [`NavLink`][vizro.models.NavLink]         | Single icon-linked entry in a `NavBar`.                                                            | [Navigation](user-guides/navigation.md)                  |
| [`Accordion`][vizro.models.Accordion]     | Grouped collapsible page list; default sidebar navigation.                                         | [Navigation](user-guides/navigation.md)                  |
| [`Action`][vizro.models.Action]           | Wraps a callable with `function`, `inputs`, `outputs`.                                             | [Actions](user-guides/actions.md)                        |
| [`VizroBaseModel`][vizro.models.VizroBaseModel] | Base class for custom components.                                                                  | [Custom components](user-guides/custom-components.md)    |

## Built-in actions (`vizro.actions`, alias `va`)

Use these instead of writing a custom action wherever the built-in fits.

| Action                                                    | Purpose                                                                                                                             | Guide                                                            |
| --------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------- |
| [`va.export_data()`][vizro.actions.export_data]           | Export filtered data of targeted components to CSV or XLSX.                                                                         | [Handle data](user-guides/data-actions.md)                       |
| [`va.set_control()`][vizro.actions.set_control]           | Set a `Filter` or `Parameter` value from a graph or table click, row selection, or another source component.                        | [Graph and table interactions](user-guides/graph-table-actions.md) |
| [`va.filter_interaction()`][vizro.actions.filter_interaction] | Legacy alias for cross-filter behavior. Prefer `va.set_control` in new code.                                                   | [Graph and table interactions](user-guides/graph-table-actions.md) |
| [`va.show_notification()`][vizro.actions.show_notification] | Show a toast notification.                                                                                                        | [Notifications](user-guides/notification-actions.md)              |
| [`va.update_notification()`][vizro.actions.update_notification] | Update an already-visible toast (progress, success, error).                                                                   | [Notifications](user-guides/notification-actions.md)              |

## Selector auto-selection

`Filter(column=...)` (and `Parameter`) picks a selector from the column dtype if `selector` is not set. Override by passing an explicit selector.

| Column dtype                       | Default selector          |
| ---------------------------------- | ------------------------- |
| numerical                          | `RangeSlider`             |
| categorical (object, string, cat)  | `Dropdown` (multi-select) |
| date / datetime                    | `DatePicker`              |
| time                               | `TimePicker`              |
| boolean                            | `Switch`                  |
| hierarchical                       | `Cascader`                |

See [filters](user-guides/filters.md) and [selectors](user-guides/selectors.md) for the full rules, disallowed combinations, and how to make dynamic filter options static.

## `@capture` decorator matrix

Every user-supplied callable that goes into a Vizro model must be wrapped with `@capture(mode)` from `vizro.models.types`.

| Mode                    | Wraps                                                     | Used in                                                                 | Guide                                                       |
| ----------------------- | --------------------------------------------------------- | ----------------------------------------------------------------------- | ----------------------------------------------------------- |
| `@capture("graph")`     | A function that returns a Plotly `Figure`.                | `Graph(figure=...)`                                                     | [Custom charts](user-guides/custom-charts.md)               |
| `@capture("table")`     | A function that returns a Dash DataTable or AG Grid.      | `Table(figure=...)` or `AgGrid(figure=...)`                             | [Custom tables](user-guides/custom-tables.md)               |
| `@capture("figure")`    | A function that returns any Dash component.               | `Figure(figure=...)`                                                    | [Custom figures](user-guides/custom-figures.md)             |
| `@capture("action")`    | A function that runs on user interaction and returns outputs. | `vm.Action(function=your_fn(...))`                                  | [Custom actions](user-guides/custom-actions.md)             |

Every `@capture`-decorated function receives its first positional argument as data:

- `@capture("graph"|"table"|"figure")` → first argument is a `data_frame: pandas.DataFrame`.
- `@capture("action")` → arguments are the values of the referenced Vizro model inputs; returns are mapped to the referenced outputs.

## What only works in Python configuration

The following features **cannot** be expressed in a YAML or JSON dashboard configuration. If a task requires any of them, you must use the Python `vm.*` API.

1. **Custom components** subclassing [`VizroBaseModel`][vizro.models.VizroBaseModel]. See [custom components](user-guides/custom-components.md).
2. **Custom actions** wrapped with `@capture("action")`. See [custom actions](user-guides/custom-actions.md).
3. **`Model.add_type(field_name, new_type)`** to widen a discriminated-union field for a custom component. See [custom components](user-guides/custom-components.md).
4. **Custom dashboard headers or overrides** (any argument that takes a Dash / dbc Python object rather than a serializable dict).
5. **Registration of `CapturedCallable`s** (`@capture("graph"|"table"|"figure"|"action")` decorators, custom `plotly` functions passed to `Graph.figure`, etc.). YAML and JSON can only reference registered names.

## Top errors and fixes

| Error                                                                                                                                                                          | Cause                                                                                                                            | Fix                                                                                                                                                                                          |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `DuplicateIDError: Model with id=<X> already exists. Models must have a unique id across the whole dashboard.`                                                                 | You re-ran the notebook or script without clearing the model registry, so Vizro sees two instances of the same id.               | Restart the kernel, or add `from vizro import Vizro; Vizro._reset()` at the top of the cell. See [notebook workflow](user-guides/run-deploy.md#develop-in-a-notebook).                       |
| `KeyError: Data source "<name>" does not exist.` when running a YAML/JSON dashboard.                                                                                           | YAML/JSON only reference data sources by name; the Python entry point did not register the data in the data manager.             | Before parsing the config, register data: `from vizro.managers import data_manager; data_manager["<name>"] = my_dataframe`. See [reference by name](user-guides/data.md#reference-by-name).  |
| `ValueError: A callable of mode "..." has been provided. Please wrap it inside "vm.<Model>(figure=<callable>(...))".`                                                          | You passed a `@capture`-decorated callable to the wrong model field.                                                             | Wrap it in the matching model: `Graph(figure=chart(...))` for `@capture("graph")`, etc. See the [decorator matrix](#capture-decorator-matrix).                                               |
| `pydantic_core.ValidationError` mentioning `discriminator` or `Input should be a valid dictionary` for a custom component.                                                     | The custom subclass has not been registered with `add_type` on the parent model's field.                                         | Call `ParentModel.add_type("field_name", MyCustomClass)` before instantiating. See [custom components](user-guides/custom-components.md).                                                     |
| `AttributeError: 'DataFrame' object has no attribute 'cache_arguments'` (or similar cache-only errors on a data source).                                                       | You called a cache-only method on data supplied directly as a DataFrame; caching applies only to registered [dynamic data](user-guides/data.md#dynamic-data). | Register the data source as a callable in `data_manager` and configure `data_manager.cache`. See [configure cache](user-guides/data.md#configure-cache).                                     |

## Machine-readable schema

A JSON Schema of the full dashboard configuration is published per Vizro version in the repo:

- **All versions**: [https://github.com/mckinsey/vizro/tree/main/vizro-core/schemas](https://github.com/mckinsey/vizro/tree/main/vizro-core/schemas)
- **Format**: files named `<version>.json` (for example, `0.1.59.json`).

For background on how the schema relates to the Python models and where its limits are, see the [schema explanation](explanation/schema.md).

## Where to go next

- [Quickstart tutorial](tutorials/quickstart-tutorial.md) — a first end-to-end dashboard.
- [Explore Vizro](tutorials/explore-components.md) — deep dive tutorial covering most components.
- [How-to guides](user-guides/dashboard.md) — task-oriented documentation for each model and feature.
- [Full model reference](API-reference/models.md) — auto-generated API reference for every `vm.*` model.
- [`llms.txt`](../llms.txt) — the discoverable index of the Vizro docs for automated tooling.
