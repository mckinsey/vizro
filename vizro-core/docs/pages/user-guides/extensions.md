# How to extend and customize Vizro dashboards

At its simplest, Vizro enables low-code configuration, but you can also customize it to go beyond its default capabilities:

* **Vizro customizations** can be used to extend the default functionality of Vizro by enabling users to create Python functions to customize charts, tables, dashboard components, callbacks in the form of actions, and reactive HTML components, then plug them directly into the existing Vizro dashboard configuration.


* **Dash customizations**, as custom Dash callbacks, can be added directly to any Vizro dashboard enabling you to code beneath the Vizro layer and control Dash directly.


* **React.js customizations** as custom React.js components can be added directly to any Vizro dashboard enabling users to go beneath both the Vizro and Dash layers and control React.js directly


This ability for extensive customization combines the ease and simplicity of Vizro configurations,
with the power go beyond that configuration and extend the dashboard functionality almost infinitely -
combining low-code and high-code approaches to provide the best of both worlds


## 1) Vizro customizations

Vizro custom functions can be used to seamlessly extend the default functionality of Vizro
by allowing users to create Python functions for customizing charts, tables, dashboard components
callbacks in the form of actions, and reactive HTML components - then plug them directly
into the existing Vizro dashboard configuration

- ### [Custom charts](custom-charts.md)

    It is possible to create custom chart functions in Vizro by wrapping Plotly chart code inside a
    Vizro chart function wrapper, and then use them directly inside Vizro dashboard configuration.
    This enables the creation of things like `plotly.graph_objects` charts with multiple traces, or `plotly_express`
    charts with post update customizations


- ### [Custom tables](custom-tables.md)

    In cases where the available arguments for the [`dash_ag_grid`][vizro.tables.dash_ag_grid] or [`dash_data_table`][vizro.tables.dash_data_table] models are not sufficient,
    you can create a custom Dash AG Grid or Dash DataTable.


- ### [Custom components](custom-components.md)

    In general, you can create a custom component based on any dash-compatible component (for example, [dash-core-components](https://dash.plotly.com/dash-core-components),
    [dash-bootstrap-components](https://dash-bootstrap-components.opensource.faculty.ai/), [dash-html-components](https://github.com/plotly/dash/tree/dev/components/dash-html-components)).

    All our components are based on `Dash`, and they are shipped with a set of sensible defaults that can be modified. If you would like to overwrite one of those defaults,
    or if you would like to use extra `args` or `kwargs` of those components, then this is the correct way to include those. You can use any existing attribute of any underlying [Dash component](https://dash.plotly.com/#open-source-component-libraries) with this method.


- ### [Custom actions](custom-actions.md)

    If you want to use the [`Action`][vizro.models.Action] model to perform functions that are not available in the [pre-defined action functions][vizro.actions], you can create your own custom action.
    Like other [actions](actions.md), custom actions could also be added as an element inside the [actions chain](actions.md#chain-actions), and it can be triggered with one of many dashboard components.


- ### [Custom figures](custom-figures.md)

    Custom figures are useful when you need a component that reacts to
    [filter](filters.md) and [parameter](parameters.md) controls.

    The [`Figure`][vizro.models.Figure] model accepts the `figure` argument, where you can enter _any_ custom figure function
    as explained in the [user guide on figures](figure.md).


## 2) Dash customizations

Since Vizro is built using Dash, it is possible to use Dash callbacks directly in any Vizro dashboard -
allowing users to go beneath the Vizro layer to control Dash directly,
which is especially useful when working with callbacks

Here is an example showing a Dash callback within Vizro,
enabling an interaction between data points in a scatter plot and the content of a text card:

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

<!-- vale off -->

## 3) React.js customizations

<!-- vale on -->

It is possible to create custom React.js components and add them
directly to any Vizro dashboard - allowing users to go beneath both the Vizro and Dash layers to control React.js directly

For more information view the documentation on [using React.js components with Dash](https://dash.plotly.com/plugins)
