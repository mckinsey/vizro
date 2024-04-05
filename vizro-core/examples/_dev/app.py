"""Example to show dashboard configuration."""

import vizro.models as vm
import vizro.plotly.express as px
from flask_caching import Cache
from vizro import Vizro
from vizro.managers import data_manager

df = px.data.iris()

# data_manager.cache = Cache(config={"CACHE_TYPE": "SimpleCache", "CACHE_DEFAULT_TIMEOUT": 20})
data_manager.cache = Cache(config={"CACHE_TYPE": "FileSystemCache", "CACHE_DIR": "cache", "CACHE_DEFAULT_TIMEOUT": 20})
# I didn't test this one yet:
# data_manager.cache = Cache(config={"CACHE_TYPE": "RedisCache"})
data_manager["default_expire_data"] = lambda: px.data.iris()

# Set cache of fast_expire_data to expire every 10 seconds
data_manager["fast_expire_data"] = px.data.iris()
# data_manager["fast_expire_data"].timeout = 5
# Set cache of no_expire_data to never expire
data_manager["no_expire_data"] = lambda: px.data.iris()
data_manager["no_expire_data"].timeout = 0

page = vm.Page(
    title="Blah",
    components=[
        vm.Graph(figure=px.scatter(df, "sepal_width", "sepal_length")),
        vm.Graph(figure=px.scatter(df, "sepal_width", "sepal_length")),
        vm.Graph(figure=px.scatter("default_expire_data", "sepal_width", "sepal_length")),
        vm.Graph(figure=px.scatter("fast_expire_data", "sepal_width", "sepal_length")),
        vm.Graph(figure=px.scatter("no_expire_data", "sepal_width", "sepal_length")),
    ],
    controls=[vm.Filter(column="species")],
)
dashboard = vm.Dashboard(pages=[page])
app = Vizro().build(dashboard)
server = app.dash.server

if __name__ == "__main__":
    app.run()
    # app.run(processes=2, threaded=False)
    # gunicorn -w 2 app:server -b localhost:8050
    # should also work with --preload
