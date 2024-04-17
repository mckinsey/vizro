# How to connect your dashboard to data

Vizro supports two different types of data:

* [Static data](#static-data): pandas DataFrame. This is the simplest method and best to use if you do not need the more advanced functionality of dynamic data.
* [Dynamic data](#dynamic-data): function that returns a pandas DataFrame. This is a bit more complex to understand but has more advanced functionality such as the ability to refresh data while the dashboard is running.

The following flowchart shows what you need to consider when choosing how to set up your data.
``` mermaid
graph TD
  refresh["`Do you need your data to refresh while the dashboard is running?`"]
  specification["`Do you need to specify your dashboard through a configuration language like YAML?`"]
  dynamic([Use dynamic data referenced by name])
  static-direct([Use static data supplied directly])
  static-name([Use static data referenced by name])

  refresh -- No --> specification
  refresh -- Yes --> dynamic
  specification -- No --> static-direct
  specification -- Yes --> static-name

  click static-direct href "#supply-directly"
  click static-name href "#reference-by-name"
  click dynamic href "#dynamic-data"

  classDef clickable color:#4051b5;
```

??? note "Static vs. dynamic data comparison"

    This table gives a full comparison between static and dynamic data. Do not worry if you do not yet understand everything in it; it will become clearer after reading more about [static data](#static-data) and [dynamic data](#dynamic-data)!

    |                                                               | Static           | Dynamic                                  |
    |---------------------------------------------------------------|------------------|------------------------------------------|
    | Required Python type                                          | pandas DataFrame | Function that returns a pandas DataFrame |
    | Can be supplied directly in `data_frame` argument of `figure` | Yes              | No                                       |
    | Can be referenced by name after adding to data manager        | Yes              | Yes                                      |
    | Can be refreshed while dashboard is running                   | No               | Yes                                      |
    | Production-ready                                              | Yes              | Yes                                      |

If you have a [Kedro](https://kedro.org/) project or would like to use the [Kedro Data Catalog](https://docs.kedro.org/en/stable/data/index.html) to manage your data independently of a Kedro project then you should use Vizro's [integration with the Kedro Data Catalog](kedro-data-catalog.md). This offers helper functions to add [`kedro_datasets.pandas`](https://docs.kedro.org/en/stable/kedro_datasets.html) as dynamic data in the Vizro data manager.

## Static data

A static data source is the simplest way to send data to your dashboard and should be used for any data that does not need to be reloaded while the dashboard is running. It is production-ready and works out of the box in a multi-process deployment. If you need data to be refreshed without restarting the dashboard then you should instead use [dynamic data](#dynamic-data).

### Supply directly

You can directly supply a pandas DataFrame into components such as [graphs](graph.md) and [tables](table.md).

The below example uses the Iris data saved to a file `iris.csv` in the same directory as `app.py`. This data can be generated using `px.data.iris()` or [downloaded](../../assets/user_guides/data/iris.csv).

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

The [`Graph`][vizro.models.Graph], [`AgGrid`][vizro.models.AgGrid] and [`Table`][vizro.models.Table] models all have an argument called `figure`. This accepts a function (in the above example, `px.scatter`) that takes a pandas DataFrame as its first argument. The name of this argument is always `data_frame`. When configuring the dashboard using Python, it is optional to give the name of the argument: if you like, you could write `data_frame=iris` instead of `iris`.
!!! note

    With static data, once the dashboard is running, the data shown in the dashboard cannot change even if the source data in `iris.csv` changes. The code `iris = pd.read_csv("iris.csv")` is only executed once when the dashboard is first started. If you would like changes to source data to flow through to the dashboard then you must use [dynamic data](#dynamic-data).

### Reference by name

If you would like to specify your dashboard configuration through YAML then you must first add your data to the data manager, importable as `vizro.managers.data_manager`. The value of the `data_frame` argument in the YAML configuration should then refer to the name of your data in the data manager.

!!! example "Static data referenced by name"
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

        1. `"iris"` is the name of a data source added to the data manager. This data is a pandas DataFrame created by reading from the CSV file `iris.csv`.
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

It is also possible to refer to a named data source using the Python API: `px.scatter("iris", ...)` or `px.scatter(data_frame="iris", ...)`  would work if the `"iris"` data source has been registered in the data manager.

## Dynamic data

A dynamic data source is a Python function that returns a pandas DataFrame. This function is executed when the dashboard is initially started and _can be executed again while the dashboard is running_. This makes it possible to refresh the data shown in your dashboard without restarting the dashboard itself. If you do not require this functionality then you should use [static data](#static-data) instead.

Unlike static data, dynamic data cannot be supplied directly into the `data_frame` argument of a `figure`. Instead, it must first be added to the data manager and then referenced by name.

The example below shows how data is fetched dynamically every time the page is refreshed. When you run the code and refresh the page the function `load_iris_data` is re-run, which returns different data each time. The example uses the Iris data saved to a file `iris.csv` in the same directory as `app.py`. This data can be generated using `px.data.iris()` or [downloaded](../../assets/user_guides/data/iris.csv).


!!! example "Dynamic data"
    === "app.py"
        ```py
        from vizro import Vizro
        import pandas as pd
        import vizro.plotly.express as px
        import vizro.models as vm

        from vizro.managers import data_manager

        def load_iris_data():
            iris = pd.read_csv("iris.csv") # (1)!
            return iris.sample(30) # (2)!

        data_manager["iris"] = load_iris_data # (3)!

        page = vm.Page(
            title="My first page",
            components=[
                vm.Graph(figure=px.scatter("iris", x="sepal_length", y="petal_width", color="species")), # (4)!
            ],
            controls=[vm.Filter(column="species")],
        )

        dashboard = vm.Dashboard(pages=[page])

        Vizro().build(dashboard).run()
        ```

        1. `iris` is a pandas DataFrame created by reading from the CSV file `iris.csv`.
        2. To demonstrate that dynamic data can change when the page is refreshed, select 30 points at random. This simulates what would happen if your file `iris.csv` were constantly changing.
        3. To use `load_iris_data` as dynamic data it must be added to the data manager. You should **not** actually call the function as `load_iris_data()`; doing so would result in static data that cannot be reloaded.
        4. Dynamic data is referenced by the name of the data source `"iris"`.

    === "Result"
        [![DynamicData]][DynamicData]

    [DynamicData]: ../../assets/user_guides/data/dynamic_data.gif

Since dynamic data sources must always be added to the data manager and referenced by name, they may be used in YAML configuration [exactly the same way as for static data sources](#reference-by-name).

### Configure cache

By default, each time the dashboard is refreshed a dynamic data function executes again. In fact, if there are multiple graphs on the same page using the same dynamic data source then the loading function executes _multiple_ times, once for each graph on the page. Hence, if loading your data is a slow operation, your dashboard performance may suffer.

The Vizro data manager has a server-side caching mechanism to help solve this. Vizro's cache uses [Flask-Caching](https://flask-caching.readthedocs.io/en/latest/), which supports a number of possible cache backends and [configuration options](https://flask-caching.readthedocs.io/en/latest/#configuring-flask-caching). By default, the cache is turned off.

<!-- vale off -->
In a development environment the easiest way to enable caching is to use a [simple memory cache](https://cachelib.readthedocs.io/en/stable/simple/) with the default configuration options. This is achieved by adding one line to the above example to set `data_manager.cache`:

!!! example "Simple cache with default timeout of 5 minutes"

    ```py hl_lines="13"
    from flask_caching import Cache
    from vizro import Vizro
    import pandas as pd
    import vizro.plotly.express as px
    import vizro.models as vm

    from vizro.managers import data_manager

    def load_iris_data():
        iris = pd.read_csv("iris.csv")
        return iris.sample(30)

    data_manager.cache = Cache(config={"CACHE_TYPE": "SimpleCache"})
    data_manager["iris"] = load_iris_data

    page = vm.Page(
        title="My first page",
        components=[
            vm.Graph(figure=px.scatter("iris", x="sepal_length", y="petal_width", color="species")),
        ],
        controls=[vm.Filter(column="species")],
    )

    dashboard = vm.Dashboard(pages=[page])

    Vizro().build(dashboard).run()
    ```



By default, when caching is turned on, dynamic data is cached in the data manager for 5 minutes. A refresh of the dashboard within this time interval will fetch the pandas DataFrame from the cache and _not_ re-run the data loading function. Once the cache timeout period has elapsed, the next refresh of the dashboard will re-execute the dynamic data loading function. The resulting pandas DataFrame will again be put into the cache and not expire until another 5 minutes has elapsed.

If you would like to alter some options, such as the default cache timeout, then you can specify a different cache configuration:

```py title="Simple cache with timeout set to 10 minutes"
data_manager.cache = Cache(config={"CACHE_TYPE": "SimpleCache", "CACHE_DEFAULT_TIMEOUT": 600})
```

!!! warning

    Simple cache exists purely for single-process development purposes and is not intended to be used in production. If you deploy with multiple workers, [for example with gunicorn](run.md/#gunicorn), then you should use a production-ready cache backend. All of Flask-Caching's [built-in backends](https://flask-caching.readthedocs.io/en/latest/#built-in-cache-backends) other than `SimpleCache` are suitable for production. In particular, you might like to use [`FileSystemCache`](https://cachelib.readthedocs.io/en/stable/file/) or [`RedisCache`](https://cachelib.readthedocs.io/en/stable/redis/):

    ```py title="Production-ready caches"
    # Store cached data in CACHE_DIR
    data_manager.cache = Cache(config={"CACHE_TYPE": "FileSystemCache", "CACHE_DIR": "cache"})

    # Use Redis key-value store
    data_manager.cache = Cache(config={"CACHE_TYPE": "RedisCache", "CACHE_REDIS_HOST": "localhost", "CACHE_REDIS_PORT": 6379})
    ```

    Since Flask-Caching relies on [`pickle`](https://docs.python.org/3/library/pickle.html), which can execute arbitrary code during unpickling, you should not cache data from untrusted sources. Doing so [could be unsafe](https://github.com/pallets-eco/flask-caching/pull/209).

Note that when a production-ready cache backend is used, the cache is persisted beyond the Vizro process and is not cleared by restarting your server. If you wish to clear the cache then you must do so manually, for example, if you use `FileSystemCache` then you would delete your `cache` directory. Persisting the cache can also be useful for development purposes when handling data that takes a long time to load: even if you do not need the data to refresh while your dashboard is running, it can speed up your development loop to use dynamic data with a cache that is persisted between repeated runs of Vizro.
<!-- vale on -->
#### Set timeouts

You can change the timeout of the cache independently for each dynamic data source in the data manager using the `timeout` setting (measured in seconds). A `timeout` of 0 indicates that the cache does not expire. This is effectively the same as using [static data](#static-data).

```py title="Set the cache timeout for each dynamic data source"
from vizro.managers import data_manager
from flask_caching import Cache

data_manager.cache = Cache(config={"CACHE_TYPE": "SimpleCache", "CACHE_DEFAULT_TIMEOUT": 600})

# Cache of default_expire_data expires every 10 minutes, the default set by CACHE_DEFAULT_TIMEOUT
data_manager["default_expire_data"] = load_iris_data

# Set cache of fast_expire_data to expire every 10 seconds
data_manager["fast_expire_data"] = load_iris_data
data_manager["fast_expire_data"].timeout = 10

# Set cache of slow_expire_data to expires every hour
data_manager["slow_expire_data"] = load_iris_data
data_manager["slow_expire_data"].timeout = 60 * 60

# Set cache of no_expire_data to never expire
data_manager["no_expire_data"] = load_iris_data
data_manager["no_expire_data"].timeout = 0
```
