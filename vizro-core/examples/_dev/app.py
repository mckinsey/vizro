"""Example to show dashboard configuration."""
import logging
from dash import ctx
from flask import request

import vizro.models as vm
import vizro.plotly.express as px
from flask_caching import Cache
from vizro import Vizro
from vizro.managers import data_manager
from vizro.models.types import capture
import pandas as pd

df = px.data.iris()


def f():
    # logging.critical(ctx)
    try:
        species = request.args["species"]
    except (RuntimeError, KeyError):
        species = "setosa"
    return px.data.iris().query("species == @species")


# data_manager.cache = Cache(config={"CACHE_TYPE": "SimpleCache", "CACHE_DEFAULT_TIMEOUT": 20})
data_manager.cache = Cache(config={"CACHE_TYPE": "FileSystemCache", "CACHE_DIR": "cache", "CACHE_DEFAULT_TIMEOUT": 20})
# I didn't test this one yet:
# data_manager.cache = Cache(config={"CACHE_TYPE": "RedisCache"})
data_manager["default_expire_data"] = f

# Set cache of fast_expire_data to expire every 10 seconds
data_manager["fast_expire_data"] = f
# data_manager["fast_expire_data"].timeout = 5
# Set cache of no_expire_data to never expire
data_manager["no_expire_data"] = lambda: pd.read_csv("file.csv")
data_manager["no_expire_data"].timeout = 0


@capture("action")
def refresh(data: str):
    data_manager[data].refresh()


page = vm.Page(
    title="Blah",
    components=[
        vm.Graph(figure=px.scatter(df, "sepal_width", "sepal_length", color="species")),
        vm.Graph(figure=px.scatter(df, "sepal_width", "sepal_length", color="species")),
        vm.Graph(figure=px.scatter("default_expire_data", "sepal_width", "sepal_length", color="species")),
        vm.Graph(figure=px.scatter("fast_expire_data", "sepal_width", "sepal_length", color="species")),
        vm.Graph(figure=px.scatter("no_expire_data", "sepal_width", "sepal_length", color="species")),
        vm.Button(text="Refresh no_expire_data", actions=[vm.Action(function=refresh("no_expire_data"))]),
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

# Check you can update/invalidate/reset memoize on demand? rather than just waiting for timeout. Use forced_update as in shelf "This is how to refresh memoize for one dataset". Previously done with delete_memoized and
# data_manager._cache.cache.clear()
