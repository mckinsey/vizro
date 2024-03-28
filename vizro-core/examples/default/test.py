"""Example to show dashboard configuration."""
import os

from flask_caching import Cache

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.managers import data_manager
from vizro.models.types import capture

import logging

log = logging.getLogger("werkzeug")
log.setLevel(logging.ERROR)


def retrieve_gapminder():
    """This is a function that returns gapminder data."""
    return px.data.gapminder()


df_gapminder = px.data.gapminder()
df_gapminder2 = px.data.gapminder()


# Options for configuring per-dataset arguments:
data_manager["gapminder_no_expire"] = retrieve_gapminder
data_manager["gapminder_no_expire"]._timeout = 0

data_manager["gapminder_default_expire"] = retrieve_gapminder

data_manager["gapminder_fast_expire"] = retrieve_gapminder
data_manager["gapminder_fast_expire"]._timeout = 5

data_manager.cache = Cache(config={"CACHE_TYPE": "SimpleCache", "CACHE_DEFAULT_TIMEOUT": 20})
# data_manager._cache = Cache(config={"CACHE_TYPE": "FileSystemCache", "CACHE_DIR": "cache", "CACHE_DEFAULT_TIMEOUT":
# 20})


@capture("action")
def refresh():
    data_manager["gapminder_default_expire"].refresh()


page = vm.Page(
    title="test_page",
    components=[
        vm.Graph(
            figure=px.box(
                "gapminder_no_expire",
                x="continent",
                y="lifeExp",
                color="continent",
                title="Distribution per continent",
            ),
        ),
        vm.Graph(
            figure=px.box(
                "gapminder_default_expire",
                x="continent",
                y="lifeExp",
                color="continent",
                title="Distribution per continent",
            ),
        ),
        vm.Graph(
            figure=px.box(
                "gapminder_fast_expire",
                x="continent",
                y="lifeExp",
                color="continent",
                title="Distribution per continent",
            ),
        ),
        vm.Button(actions=[vm.Action(function=refresh())]),
    ],
)
dashboard = vm.Dashboard(pages=[page])

# ### when launching with gunicorn ###
# Vizro._user_assets_folder = os.path.abspath("../assets")
# data_manager._cache.config = {
#     "CACHE_TYPE": "FileSystemCache",
#     "CACHE_DIR": "cache",
#     "CACHE_THRESHOLD": 20,  # The maximum number of items the cache can hold
#     "CACHE_DEFAULT_TIMEOUT": 3000,  # Unit of time is seconds
# }
# data_manager._cache.config = {
#     "CACHE_TYPE": "RedisCache",
#     "CACHE_REDIS_URL": "redis://localhost:6379/0",
#     "CACHE_DEFAULT_TIMEOUT": 120,
# }
# app = Vizro()
# app.build(dashboard)
# server = app.dash.server
# ### when launching with gunicorn ###
app = Vizro().build(dashboard)
server = app.dash.server
if __name__ == "__main__":
    Vizro._user_assets_folder = os.path.abspath("../assets")
    # data_manager._cache.config = {
    #     "CACHE_TYPE": "FileSystemCache",
    #     "CACHE_DIR": "cache",
    #     "CACHE_THRESHOLD": 20,  # The maximum number of items the cache can hold
    #     "CACHE_DEFAULT_TIMEOUT": 3000,  # Unit of time is seconds
    # }
    # data_manager._cache.config = {
    #     "CACHE_TYPE": "RedisCache",
    #     "CACHE_REDIS_URL": "redis://localhost:6379/0",
    #     "CACHE_DEFAULT_TIMEOUT": 60,
    app.run(processes=2, threaded=False)
    # app.run()
    # Vizro().build(dashboard).run(
    #     threaded=False,
    #     processes=3,
    #     dev_tools_hot_reload=False
    # )
