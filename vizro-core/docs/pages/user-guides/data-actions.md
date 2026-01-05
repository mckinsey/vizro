# How to use actions to handle data

## Export data

To download data from your dashboard, you can use the [`export_data` action][vizro.actions.export_data]. For example, you can attach the action to a [button](button.md) as follows. When a user clicks the "Export data" button, all data on the page is downloaded.

!!! example "Export data action"

    === "app.py"

        ```{.python pycafe-link hl_lines="12"}
        import vizro.actions as va
        import vizro.models as vm
        import vizro.plotly.express as px
        from vizro import Vizro

        df = px.data.iris()

        page = vm.Page(
            title="Action triggered by a button",
            components=[
                vm.Graph(figure=px.histogram(df, x="sepal_length")),
                vm.Button(text="Export data", actions=va.export_data()),
            ],
            controls=[vm.Filter(column="species")],
        )

        dashboard = vm.Dashboard(pages=[page])
        Vizro().build(dashboard).run()
        ```

    === "app.yaml"

        ```yaml
        # Still requires a .py to add data to the data manager and parse YAML configuration
        # See yaml_version example
        pages:
          - components:
              - type: graph
                figure:
                  _target_: histogram
                  x: sepal_length
              - type: button
                text: Export data
                actions:
                  - type: export_data
          - controls:
              - type: filter
                column: species
            layout:
              type: flex
            title: Action triggered by a button
        ```

    === "Result"

        [![ExportData]][exportdata]

When you click the "Export data" button, the data for all graphs, tables and figures on the page is downloaded. In this example, this will produce a csv file for the graph's source data `px.data.iris()`.

Exported data includes the effect of [controls](controls.md) such as [filters](filters.md) and [dynamic data parameters](parameters.md#dynamic-data-parameters). Modifications from the chart, table or figure itself are not included (for example, AG Grid filters, graph zoom and data transformations performed inside a [custom chart functions](custom-charts.md)).

[exportdata]: ../../assets/user_guides/actions/actions_export.png
