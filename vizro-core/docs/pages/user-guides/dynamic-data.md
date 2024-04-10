# Dynamic data

A dynamic data source is a Python function that returns a pandas DataFrame. This function is executed when the dashboard is initially started and _can be executed again while the dashboard is running_. This makes it possible to refresh the data shown in your dashboard without restarting the dashboard itself. If you do not require this functionality then you should use [static data](static-data.md) instead.

Unlike static data, dynamic data cannot be supplied directly into the `data_frame` argument of a `figure`. Instead, it must first be added to the Data Manager and then referenced by name.

The below toy example demonstrates how dynamic data is updated every time the page is refreshed. When you run the code and refresh the page the data shown will change every time because the function `load_iris_data` is re-run. The example uses the Iris dataset saved to a file `iris.csv` in the same directory as `app.py`. This data can be generated using `px.data.iris()` or [downloaded](../../assets/user_guides/data/iris.csv).

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
        3. To use `load_iris_data` as dynamic data it must be added to the Data Manager. You should **not** actually call the function as `load_iris_data()`; doing so would result in static data that cannot be reloaded.
        4. Dynamic data is referenced by the name of the data source `"iris"`.

    === "Result"
        [![DataBasic]][DataBasic]

    [DataBasic]: ../../assets/user_guides/data/data_pandas_dataframe.png

Since dynamic data sources must always be added to the Data Manager and referenced by name, they may be used in YAML configuration [exactly the same way as for static data sources](static-data.md#reference-by-name).

## Configure cache

By default, every time the dashboard is refreshed a dynamic data function will be executed again. This means that your dashboard will always show the very latest data. In fact, if there are multiple graphs on the same page using the same dynamic data source then the loading function will be executed _multiple_ times, once for each graph on the page. Hence, if loading your data is a slow operation, your dashboard performance may suffer.

The Vizro Data Manager has a server-side caching mechanism to help solve this. Vizro's cache uses [Flask-Caching](https://flask-caching.readthedocs.io/en/latest/), which supports a number of possible cache backends and [configuration options](https://flask-caching.readthedocs.io/en/latest/#configuring-flask-caching). By default, the cache is turned off. 

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


By default, when caching is turned on, dynamic data is cached in the Data Manager for 5 minutes. A refresh of the dashboard within this time interval will fetch the pandas DataFrame from the cache and _not_ re-run the data loading function. Once the cache timeout period has elapsed, the next refresh of the dashboard will re-execute the dynamic data loading function. The resulting pandas DataFrame will again be put into the cache and not expire until another 5 minutes has elapsed.

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

Note that when a production-ready cache backend is used, the cache is persisted beyond the Vizro process and is not cleared by restarting your server. If you wish to clear the cache then you must do so manually, e.g. if you use `FileSystemCache` then you would delete your `cache` directory. Persisting the cache can also be useful for development purposes when handling data that takes a long time to load: even if you do not need the data to refresh while your dashboard is running, it can speed up your development loop to use dynamic data with a cache that is persisted between repeated runs of Vizro.

### Set timeouts

You can change the timeout of the cache independently for each dynamic data source in the Data Manager using the `timeout` setting (measured in seconds). A `timeout` of 0 indicates that the cache does not expire. This is effectively the same as using [static data](static-data.md).
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
