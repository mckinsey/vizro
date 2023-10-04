# How to connect your dashboard to data

This guide shows you how to connect your dashboard and your charts within the dashboard to data.

Vizro provides two ways to connect your charts to data. This section shows you how to use both.

## Directly feed a Pandas DataFrame to your chart

You can directly feed a Pandas DataFrame to your chart. This is the simplest way to connect your charts to data.

!!! example "Feed a Pandas DataFrame"
    === "app.py"
        ```py linenums="1"
        from vizro import Vizro
        import vizro.plotly.express as px
        import vizro.models as vm

        iris = px.data.iris()

        page = vm.Page(
            title="My first page",
            components=[
                vm.Graph(id="scatter_chart", figure=px.scatter(iris, x="sepal_length", y="petal_width", color="species")),
            ],
        )

        dashboard = vm.Dashboard(pages=[page])

        Vizro().build(dashboard).run()
        ```
    === "Result"
        [![DataBasic]][DataBasic]

    [DataBasic]: ../../assets/user_guides/data/data_pandas_dataframe.png

Here `px.data.iris()` returns a Pandas DataFrame. We then pass this DataFrame to the `figure` argument of the `Graph` component.

!!! note

    If you are using JSON or YAML to define your dashboard, you can only use the
    data connector approach to connect your data.



## Use a data connector

You can also connect your charts with a data connector. To use a data connector with
Vizro, you need:

1. Define a data connector. A data connector is a function
   that returns a Pandas DataFrame. In this function, you can define how to load your
   data and then convert it to a Pandas DataFrame if necessary.

2. Register this function with the Vizro [Data Manager][vizro.managers._data_manager].
   This allows you to use this data connector
   in your dashboard.

!!! example "Use a Data Connector"
    === "app.py"
        ```py linenums="1"  hl_lines="18"
        from vizro import Vizro
        import vizro.plotly.express as px
        import vizro.models as vm
        from vizro.managers import data_manager


        # define a data connector
        def retrieve_iris():
            """This is a function that returns a Pandas DataFrame."""
            return px.data.iris()

        # register the data connector with Vizro Data Manager
        data_manager["iris"] = retrieve_iris

        page = vm.Page(
            title="My first page",
            components=[
                vm.Graph(id="scatter_chart", figure=px.scatter("iris", x="sepal_length", y="petal_width", color="species")),
            ],
            controls=[vm.Filter(column="species")],
        )

        dashboard = vm.Dashboard(pages=[page])

        Vizro().build(dashboard).run()
        ```
    === "app.yaml"
        ```yaml linenums="1" hl_lines="6"
        # Still requires a .py to register data connector in Data Manager and parse yaml configuration - see from_yaml example
        pages:
        - components:
            - figure:
                _target_: scatter
                data_frame: iris
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
    === "Result"
        [![DataConnector]][DataConnector]

    [DataConnector]: ../../assets/user_guides/data/data_pandas_dataframe.png

!!! note

    When you use a data connector, you reference the data by string. In the example, we
    use `px.scatter("iris", x="sepal_length", y="petal_width", color="species")` to reference
    the data. The string `"iris"` is the dataset name registered in Data Manager. This is
    how Vizro knows which data connector to use.


### Data connector with arguments

You can also define a data connector with arguments. This is useful when you want to
use the same data connector to load different data. For example, when you want to
retrieve data from different tables in a database, you can define a data connector
that accepts different SQL queries as arguments.

!!! example "Use a Data Connector with Arguments"
    === "app.py (use lambda)"
        ```py linenums="1"
        from vizro import Vizro
        import vizro.plotly.express as px
        import vizro.models as vm
        from vizro.managers import data_manager


        def retrieve_one_species(species):
            df = px.data.iris()
            subset = df[df["species"] == species].copy()
            return subset


        data_manager["species_setosa"] = lambda: retrieve_one_species("setosa")

        page = vm.Page(
            title="My first page",
            components=[
                vm.Graph(id="scatter_chart", figure=px.scatter("species_setosa", x="sepal_length", y="petal_width", color="species")),
            ],
            controls=[vm.Filter(column="species")],
        )

        dashboard = vm.Dashboard(pages=[page])

        Vizro().build(dashboard).run()
        ```
    === "app.py (use functools.partial)"
        ```py linenums="1"
        from functools import partial

        from vizro import Vizro
        import vizro.plotly.express as px
        import vizro.models as vm
        from vizro.managers import data_manager


        def retrieve_one_species(species):
            df = px.data.iris()
            subset = df[df["species"] == species].copy()
            return subset


        data_manager["species_setosa"] = partial(retrieve_one_species, "setosa")

        page = vm.Page(
            title="My first page",
            components=[
                vm.Graph(id="scatter_chart", figure=px.scatter("species_setosa", x="sepal_length", y="petal_width", color="species")),
            ],
            controls=[vm.Filter(column="species")],
        )

        dashboard = vm.Dashboard(pages=[page])

        Vizro().build(dashboard).run()
        ```
    === "Result"
        [![DataConnector]][DataConnector]

    [DataConnector]: ../../assets/user_guides/data/data_selected_from_source.png


### Kedro data catalog

If the data you are visualizing is a [`kedro_datasets.pandas`](https://docs.kedro.
org/en/stable/kedro_datasets.html) type from a Kedro data catalog, you can leverage
Vizro's [Kedro integration](integration.md#kedro) to connect your charts to the data catalog.

If it is not a `kedro_datasets.pandas` type, you need to build a
data connector to load the data from the data catalog and convert it to a Pandas
DataFrame, before you can register it with Vizro Data Manager.
