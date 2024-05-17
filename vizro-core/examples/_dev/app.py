"""Dev app to try things out."""
from flask_caching import Cache

import numpy as np
import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.managers import data_manager


def conf(title=""):
    return {
        'x': 'gdpPercap',
        'y': 'lifeExp',
        'color': 'continent',
        'title': title,
    }


def get_data_function():
    return px.data.gapminder().sample(20)


data_manager["static_df"] = px.data.gapminder()
data_manager["dynamic_df"] = get_data_function
data_manager["dynamic_df_2"] = get_data_function

# data_manager["dynamic_df"] = lambda: px.data.gapminder().sample(20)
# data_manager["dynamic_df_2"] = lambda: px.data.gapminder().sample(20)


data_manager.cache = Cache(config={"CACHE_TYPE": "SimpleCache"})
# data_manager.cache = Cache(config={"CACHE_TYPE": "RedisCache", "CACHE_REDIS_HOST": "localhost", "CACHE_REDIS_PORT": 6379})
# data_manager["dynamic_df"].timeout = 30
# data_manager["dynamic_df_2"].timeout = 10


page = vm.Page(
    title="Data Manager",
    layout=vm.Layout(grid=[
        [0, 1],
        [2, 3],
        [4, 5],
    ]),
    components=[
        vm.Graph(id="graph_static_direct_1", figure=px.scatter(data_frame=px.data.gapminder(), **conf("Static direct 1"))),
        vm.Graph(id="graph_static_direct_2", figure=px.scatter(data_frame=px.data.gapminder(), **conf("Static direct 2"))),
        vm.Graph(id="graph_static_dm_1", figure=px.scatter(data_frame="static_df", **conf("Static DM 1"))),
        vm.Graph(id="graph_static_dm_2", figure=px.scatter(data_frame="static_df", **conf("Static DM 2"))),
        vm.Graph(id="graph_dynamic_dm_1", figure=px.scatter(data_frame="dynamic_df", **conf("Dynamic DM 1"))),
        vm.Graph(id="graph_dynamic_dm_2", figure=px.scatter(data_frame="dynamic_df_2", **conf("Dynamic DM 2"))),
    ],
    controls=[
        vm.Filter(column="continent")
    ],
)

dashboard = vm.Dashboard(pages=[page])
app = Vizro().build(dashboard)
server = app.dash.server

if __name__ == "__main__":
    app.run()
