# Static data

A static data source is the simplest way to provide data to your dashboard and should be used for any data that does not need to be reloaded while the dashboard is running. It is production-ready and works out of the box in a multi-process deployment. If you need data that can be refreshed without restarting the dashboard then you should use [dynamic data](dynamic-data.md).

## Supply directly

You can directly supply a pandas DataFrame into components such as [graphs](graph.md) and [tables](table.md).

!!! example "Static data supplied directly"
    === "app.py"
        ```py
        from vizro import Vizro
        import pandas as pd
        import vizro.plotly.express as px
        import vizro.models as vm

        iris = pd.read_csv("iris.csv") # (1)!

        page = vm.Page(
            title="My first page",
            components=[
                vm.Graph(figure=px.scatter(iris, x="sepal_length", y="petal_width", color="species")),
            ],
            controls=[vm.Filter(column="species")],
        )

        dashboard = vm.Dashboard(pages=[page])

        Vizro().build(dashboard).run()
        ```

        1. `iris` is a pandas DataFrame created by reading from the CSV file `iris.csv`.
    === "Result"
        [![DataBasic]][DataBasic]

    [DataBasic]: ../../assets/user_guides/data/data_pandas_dataframe.png

The [`Graph`][vizro.models.Graph], [`AgGrid`][vizro.models.AgGrid] and [`Table`][vizro.models.Table] models all have an argument called `figure`. This accepts a function (in the above example, `px.scatter`) which always takes a pandas DataFrame as its first argument. The name of this argument is always `data_frame`. When configuring the dashboard using Python, it is optional to give the name of the argument (so you could write `data_frame=iris`); when specifying the dashboard configuration through YAML, the argument name must be given.

!!! note

    With static data, once the dashboard is running, the data shown in the dashboard cannot change even if the source data in `iris.csv` changes. The code `iris = pd.read_csv("iris.csv")` is only executed once when the dashboard is first started. If you would like changes to source data to flow through to the dashboard then you must use [dynamic data](dynamic-data.md).

## Reference by name

If you would like to specify your dashboard configuration through YAML then you must first add your data to the Data Manager. The value of the `data_frame` argument in the YAML configuration should then refer to the name of your data in the Data Manager.

!!! example "Static data referred to by name"
    === "app.py"
        ```py
        import yaml

        from vizro import Vizro
        import vizro.plotly.express as px
        import vizro.models as vm
        import pandas as pd
        from vizro.managers import data_manager

        data_manager["iris"] = pd.read_csv("iris.csv") # (1)!

        dashboard = yaml.safe_load(Path("dashboard.yaml").read_text(encoding="utf-8"))
        dashboard = Dashboard(**dashboard)

        Vizro().build(dashboard).run()
        ```

        1. `"iris"` is the name of a data source added to the Data Manager. This data is a pandas DataFrame created by reading from the CSV file `iris.csv`.
    === "dashboard.yaml"
        ```yaml
        pages:
        - components:
            - figure:
                _target_: scatter
                data_frame: iris # (1)!
                x: sepal_length
                y: petal_width
                color: species
              id: scatter_chart
              type: graph
            controls:
              - column: species
                type: filter
            title: My first page
        ```

        1. Refer to the `"iris"` data source in the data manager.
    === "Result"
        [![DataBasic]][DataBasic]

    [DataBasic]: ../../assets/user_guides/data/data_pandas_dataframe.png

It is also possible to refer to a named data source using the Python API: `px.scatter("iris", ...)` would work if the `"iris"` data source has been registered in the Data Manager. In fact, when it comes to dynamic data, using the data source name is the _only_ way to refer to a data source.
