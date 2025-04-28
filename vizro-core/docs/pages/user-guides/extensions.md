# How to extend and customize Vizro dashboards

At its simplest, Vizro enables low-code configuration, but you can also customize it to go beyond its default capabilities by incorporating any Dash component, Dash callback, or Plotly chart.

- **[Vizro customizations](#vizro-customizations)**. You can customize Vizro to extend the default functionality of Vizro and create Python functions as customized Plotly charts, tables, dashboard components, actions, or reactive HTML components, and then plug them directly into the existing Vizro dashboard configuration (as explained below).

- **[Dash customizations](#dash-customizations)**. You can add custom Dash callbacks directly to any Vizro dashboard, enabling you to code beneath the Vizro layer and control Dash directly.

- **[CSS customizations](#css-customizations)**. You can add custom CSS to any Vizro dashboard, enabling users to deviate from the default styling and create a unique look and feel for their dashboard.

- **[React.js customizations](#reactjs-customizations)**. You can add custom React.js components directly to any Vizro dashboard, enabling users to go beneath both the Vizro and Dash layers and control React.js directly

Vizro offers the ability to combine ease of use of low-code configuration, with the flexibility of a range of high-code extensions to expand your dashboard's functionality.

## Vizro customizations

### [Custom charts](custom-charts.md)

You can create custom chart functions in Vizro by wrapping Plotly chart code inside a Vizro chart function wrapper, and then use the functions directly inside the Vizro dashboard configuration. This enables the creation of `plotly.graph_objects` charts with multiple traces, or `plotly_express` charts with post update customizations

### [Custom tables](custom-tables.md)

If the available arguments for the [`dash_ag_grid`][vizro.tables.dash_ag_grid] or [`dash_data_table`][vizro.tables.dash_data_table] models are insufficient, you can create a custom Dash AG Grid or Dash DataTable.

### [Custom components](custom-components.md)

You can create a custom component based on any dash-compatible component (for example, [dash-core-components](https://dash.plotly.com/dash-core-components), [dash-bootstrap-components](https://dash-bootstrap-components.opensource.faculty.ai/), [dash-html-components](https://github.com/plotly/dash/tree/dev/components/dash-html-components)).

All Vizro's components are based on `Dash` and ship with a set of defaults that can be modified. If you would like to overwrite one of those defaults, or if you would like to use extra `args` or `kwargs` of those components, then this is the correct way to include those. You can use any existing attribute of any underlying [Dash component](https://dash.plotly.com/#open-source-component-libraries) with this method.

### [Custom actions](custom-actions.md)

If you want to use the [`Action`][vizro.models.Action] model to perform functions that are not available in the [built-in action functions][vizro.actions], you can create your own custom action. Like other [actions](actions.md), custom actions can also be added as an element inside the [actions chain](actions.md#chain-actions), and triggered with one of dashboard components.

### [Custom figures](custom-figures.md)

Custom figures are useful when you need a component that reacts to [filter](filters.md) and [parameter](parameters.md) controls.

Vizro's [`Figure`][vizro.models.Figure] model accepts the `figure` argument, where you can enter _any_ custom figure function as described in the [how-to guide for figures](figure.md).

## Dash customizations

Since Vizro is built using Dash, it is possible to use [Dash callbacks](https://dash.plotly.com/basic-callbacks) directly in any Vizro dashboard. This enables you to code beneath the Vizro layer and control Dash directly, which is especially useful when working with callbacks

Here is an example showing a Dash callback within Vizro, enabling an interaction between data points in a scatter plot and the content of a text card:

!!! example "Dash callback example"

    === "app.py"

        ```{.python pycafe-link}
        from dash import callback, Input, Output
        import vizro.models as vm
        import vizro.plotly.express as px
        from vizro import Vizro

        @callback(
            Output("card_id", "children"),
            Input("source_chart", "clickData")
        )
        def update_card(click_data):
            if click_data is None:
                return "Click on the graph to select a data point."
            return f"Clicked species: '{click_data['points'][0]['customdata'][0]}'"

        page = vm.Page(
            title="Example: Dash callback within Vizro",
            components=[
                vm.Graph(id="source_chart",
                         figure=px.scatter(px.data.iris(), x="sepal_width", y="sepal_length", color="species", custom_data=["species"])),
                vm.Card(id="card_id",
                        text="Click on the graph to apply filter interaction."),
            ]
        )

        dashboard = vm.Dashboard(pages=[page])
        Vizro().build(dashboard).run()
        ```

## CSS customizations

Vizro is opinionated about visual formatting, and some elements, such as the layout of the navigation and controls, are fixed. You can customize some settings such as background colors, fonts, and other styles via CSS overrides.

For more information, see our documentation on [customizing CSS](custom-css.md)

## React.js customizations

It is possible to create custom React.js components and add them directly to any Vizro dashboard so enabling you to code beneath both the Vizro and Dash layers and control React.js directly

For more information, see the documentation on [using React.js components with Dash](https://dash.plotly.com/plugins)
