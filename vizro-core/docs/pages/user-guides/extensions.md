# How to create custom functionality

Vizro provides the ability to extensively customise a wide range of functioanlity,
and go far beyond the default Vizro capabilities

1) **Vizro custom functions** - can be used to seamlessly extend the default functionality of Vizro
by allowing users to quickly create Python functions for customising charts, tables, dashboard components
callbacks in the form of actions, and reactive HTML components - then easily plug them directly
into the existing Vizro dashboard configuration

   
2) **Dash custom functions** - it is easy to create custom Dash callbacks and add them
directly to any Vizro dashboard - allowing users to go beneath the Vizro layer to control Dash directly


3) **React custom components** - it is possible to create custom Reach components and add them
directly to any Vizro dashboard - allowing users to go beneath both the Vizro and Dash layers to control Reach directly

## 1) Vizro custom functions

Vizro custom functions can be used to seamlessly extend the default functionality of Vizro
by allowing users to quickly create Python functions for customising charts, tables, dashboard components
callbacks in the form of actions, and reactive HTML components - then easily plug them directly
into the existing Vizro dashboard configuration

- ### Custom charts

blurb

[link](custom-charts.md)

- ### Custom tables

In cases where the available arguments for the [`dash_ag_grid`][vizro.tables.dash_ag_grid] or [`dash_data_table`][vizro.tables.dash_data_table] models are not sufficient,
you can create a custom Dash AG Grid or Dash DataTable.

[link](custom-tables.md)

- ### Custom components

In general, you can create a custom component based on any dash-compatible component (for example, [dash-core-components](https://dash.plotly.com/dash-core-components),
[dash-bootstrap-components](https://dash-bootstrap-components.opensource.faculty.ai/), [dash-html-components](https://github.com/plotly/dash/tree/dev/components/dash-html-components)).

All our components are based on `Dash`, and they are shipped with a set of sensible defaults that can be modified. If you would like to overwrite one of those defaults,
or if you would like to use extra `args` or `kwargs` of those components, then this is the correct way to include those. You can use any existing attribute of any underlying [Dash component](https://dash.plotly.com/#open-source-component-libraries) with this method.


[link](custom-components.md)

- ### Custom actions

If you want to use the [`Action`][vizro.models.Action] model to perform functions that are not available in the [pre-defined action functions][vizro.actions], you can create your own custom action.
Like other [actions](actions.md), custom actions could also be added as an element inside the [actions chain](actions.md#chain-actions), and it can be triggered with one of many dashboard components.


[link](custom-actions.md)

- ### Custom figures

Custom figures are useful when you need a component that reacts to
[filter](filters.md) and [parameter](parameters.md) controls.

The [`Figure`][vizro.models.Figure] model accepts the `figure` argument, where you can enter _any_ custom figure function
as explained in the [user guide on figures](figure.md).


[link](custom-figures.md)

## 2) Dash custom functions

It is easy to create custom Dash callbacks and add them
directly to any Vizro dashboard - allowing users to go beneath the Vizro layer to control Dash directly

[link]()

## 3) React custom components 

It is possible to create custom Reach components and add them
directly to any Vizro dashboard - allowing users to go beneath both the Vizro and Dash layers to control Reach directly

https://dash.plotly.com/plugins