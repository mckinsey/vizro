# How to use tables

This guide shows you how to use tables to visualize your data in the dashboard.

The [`Page`][vizro.models.Page] models accepts the `components` argument, where you can enter your visual content e.g.
[`Graph`][vizro.models.Graph], [`Table`][vizro.models.Table], [`Card`][vizro.models.Card] or [`Button`][vizro.models.Button].

## Table

The [`Table`][vizro.models.Table] model allows you to visualize data in a tabular format.

To add a [`Table`][vizro.models.Table] to your page, do the following:

- insert the [`Table`][vizro.models.Table] model into the `components` argument of the
[`Page`][vizro.models.Page] model
- enter any of the currently available table functions

See below for an overview of currently supported table functions.

### Dash DataTable

The [Dash DataTable](https://dash.plotly.com/datatable) is an interactive table component designed for viewing, editing, and exploring large datasets.

You can use the [Dash DataTable](https://dash.plotly.com/datatable) in Vizro by importing
```py
from vizro.tables import dash_data_table
```
The Vizro version of the table differs in one way from the original table: it requires the user to provide a pandas dataframe as source of data.
This must be entered under the argument `data_frame`.
All other [parameters of the Dash DataTable](https://dash.plotly.com/datatable/reference) can be entered as kwargs.

!!! example "Dash DataTable"
    === "app.py"
        ```py
        import vizro.models as vm
        from vizro import Vizro
        import vizro.plotly.express as px
        from vizro.tables import dash_data_table

        df = px.data.iris()

        page = vm.Page(
            title="Dash DataTable",
            components=[
                vm.Table(id="table", figure=dash_data_table(data_frame=df)),
            ],
            controls=[vm.Filter(column="species")],
        )
        dashboard = vm.Dashboard(pages=[page])

        Vizro().build(dashboard).run()
        ```
    === "app.yaml"
        ```yaml
        # Still requires a .py to register data connector in Data Manager and parse yaml configuration
        # See from_yaml example
        pages:
        - components:
          - figure:
              _target_: dash_data_table
              data_frame: iris
            id: table
            type: table
          controls:
            - column: species
              type: filter
          title: Dash DataTable
        ```
    === "Result"
        [![Table]][Table]

    [Table]: ../../assets/user_guides/table/table.png

#### Styling/Modifying the Dash DataTable

Lorem ipsum

#### Custom Table

Lorem Ispum
