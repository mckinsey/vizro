# How to interact with data

## Export data

To download data from your dashboard, you can use the [`export_data` action][vizro.actions.export_data]. For example, you can attach the action to a [button](button.md) as follows. When a clicks the "Export data" button, all data on the page is downloaded.

!!! example "Export data"

    === "app.py" 

        ```{.python pycafe-link hl_lines="23"}
        import vizro.actions as va
        import vizro.models as vm
        import vizro.plotly.express as px
        from vizro import Vizro

        df = px.data.iris()

        page = vm.Page(
            title="My first page",
            layout=vm.Flex(),  # (1)!
            components=[
                vm.Graph(
                    figure=px.scatter(
                        df,
                        x="sepal_width",
                        y="sepal_length",
                        color="species",
                        size="petal_length",
                    ),
                ),
                vm.Button(
                    text="Export data",
                    actions=va.export_data(),
                ),
            ]
        )

        dashboard = vm.Dashboard(pages=[page])
        Vizro().build(dashboard).run()
        ```

        1. We use a [`Flex`][vizro.models.Flex] layout to make sure the `Graph` and `Button` only occupy as much space as they need, rather than being distributed evenly.

    === "app.yaml"

        ```yaml
        # Still requires a .py to add data to the data manager and parse YAML configuration
        # See yaml_version example
        pages:
          - components:
              - figure:
                  _target_: scatter
                  x: sepal_width
                  y: sepal_length
                  color: species
                  size: petal_length
                  data_frame: iris
                type: graph
              - type: button
                text: Export data
                id: export_data
                actions:
                  - type: export_data
            layout:
              type: flex
            title: My first page
        ```

    === "Result"

        [![ExportData]][exportdata]

When you click the "Export data" button, the data for all graphs, tables and figures on the page is downloaded. In this example, this will produce a csv file for the graph's source data `px.data.iris()`.

Exported data only reflects the original data after it has been acted upon by [controls](controls.md). Modifications from the chart, table or figure itself are not included (for example, Ag Grid filters and data transformations performed inside [custom chart functions](custom-charts.md).

[exportdata]: ../../assets/user_guides/actions/actions_export.png
