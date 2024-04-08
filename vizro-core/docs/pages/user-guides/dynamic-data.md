# Dynamic data

A dynamic data source is a Python function that returns a pandas DataFrame. This function is executed when the dashboard is initially started and _can be executed again while the dashboard is running_. This makes it possible to refresh the data shown in your dashboard without restarting the dashboard itself. If you do not this functionality then you should use [static data](static-data.md) instead.

Unlike static data, dynamic data cannot be supplied directly into the `data_frame` argument of a `figure`. Instead, it must first be added to the Data Manager and then referenced by name.

!!! example "Dynamic data"
    === "app.py"
        ```py
        from vizro import Vizro
        import pandas as pd
        import vizro.plotly.express as px
        import vizro.models as vm

        from vizro.managers import data_manager

        def load_iris_data():
            return pd.read_csv("iris.csv")

        data_manager["iris"] = load_iris_data # (1)!

        page = vm.Page(
            title="My first page",
            components=[
                vm.Graph(figure=px.scatter("iris", x="sepal_length", y="petal_width", color="species")), # (2)!
            ],
            controls=[vm.Filter(column="species")],
        )

        dashboard = vm.Dashboard(pages=[page])

        Vizro().build(dashboard).run()
        ```

        1. To use `load_iris_data` as dynamic data it must first be added to the Data Manager. You should **not** actually call the function as `load_iris_data()`; doing so would result in static data that cannot be reloaded.
        2. Dynamic data is referenced by the name of the data source `"iris"`.

    === "Result"
        [![DataBasic]][DataBasic]

    [DataBasic]: ../../assets/user_guides/data/data_pandas_dataframe.png

Since dynamic data sources must always be added to the Data Manager and referenced by name, they may be used in YAML configuration [exactly the same way as for static data sources](static-data.md#reference-by-name).

## Configure cache

By default, every time the dashboard is refreshed a dynamic data function will be executed again. This means that your dashboard will always show the very latest data. In fact, if there are multiple graphs on the same page using the same dynamic data source then the loading function will be executed _multiple_ times, once for each graph on the page. Hence, if loading your data is a slow operation, your dashboard performance may suffer.

The Vizro Data Manager has a server-side caching mechanism to help solve this. Vizro's cache uses [Flask-Caching](https://flask-caching.readthedocs.io/en/latest/), which supports a number of possible cache backends and [configuration options](https://flask-caching.readthedocs.io/en/latest/#configuring-flask-caching). By default, the cache is turned off. 

In a development environment the easiest way to enable caching is to use a [simple memory cache](https://cachelib.readthedocs.io/en/stable/simple/) with the default configuration options:

```py title="Simple cache with default timeout of 5 minutes"
from flask_caching import Cache

data_manager.cache = Cache(config={"CACHE_TYPE": "SimpleCache"})
data_manager["iris"] = load_iris_data
```

By default, dynamic data is cached in the Data Manager for 5 minutes. A refresh of the dashboard within this time interval will fetch the pandas DataFrame from the cache and not re-run the data loading function. Once the cache timeout period has elapsed, the next refresh of the dashboard will re-execute the dynamic data loading function. The resulting pandas DataFrame will again be put into the cache and not expire until another 5 minutes has elapsed.

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

### Configure timeouts

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
