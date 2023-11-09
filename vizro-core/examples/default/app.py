"""Example to show dashboard configuration."""
import os
import pandas as pd

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.managers import data_manager
from vizro.models.types import capture


def retrieve_gapminder():
    """This is a function that returns gapminder data."""
    return px.data.gapminder()


df_gapminder = px.data.gapminder()
df_gapminder2 = px.data.gapminder()


# Options for configuring per-dataset arguments:
data_manager["gapminder"] = retrieve_gapminder
print("to update per dataset cache config")
data_manager["gapminder"]._cache_arguments = {"timeout": 600}
print(f"_cache_arguments: {data_manager['gapminder']._cache_arguments}")

data_manager["gapminder2"] = retrieve_gapminder
print("to update per dataset cache config")
data_manager["gapminder2"]._cache_arguments = {
    "timeout": 0,
    # "unless": (lambda: True)
}
print(f"_cache_arguments: {data_manager['gapminder2']._cache_arguments}")

@capture("action")
def delete_memoized_cache(delete_button_id_n_clicks):
    """Delete one memoized cache."""
    if delete_button_id_n_clicks:
        data_manager._cache.delete_memoized(data_manager._get_original_data, data_manager, "gapminder")


@capture("action")
def empty_cache(empty_button_id_n_clicks):
    """Empty the entire cache."""
    if empty_button_id_n_clicks:
        data_manager._cache.cache.clear()


page = vm.Page(
    title="test_page",
    components=[
        vm.Graph(
            figure=px.box(
                "gapminder",
                # df_gapminder,
                x="continent",
                y="lifeExp",
                color="continent",
                title="Distribution per continent",
            ),
            id="the_graph",
        ),
        vm.Graph(
            id="the_graph2",
            figure=px.scatter(
                "gapminder2",
                # df_gapminder2,
                x="gdpPercap",
                y="lifeExp",
                size="pop",
                color="continent",
                hover_name="country",
                facet_col="continent",
                labels={
                    "gdpPercap": "GDP per capita",
                    "pop": "Population",
                    "lifeExp": "Life expectancy",
                    "continent": "Continent",
                },
                range_y=[25, 90],
                color_discrete_map={
                    "Africa": "#00b4ff",
                    "Americas": "#ff9222",
                    "Asia": "#3949ab",
                    "Europe": "#ff5267",
                    "Oceania": "#08bdba",
                },
            ),
        ),
        vm.Button(
            id="delete_button_id",
            text="delete_memoized_cache",
            actions=[
                vm.Action(
                    function=delete_memoized_cache(),
                    inputs=["delete_button_id.n_clicks"],
                )
            ],
        ),
        vm.Button(
            id="empty_button_id",
            text="empty_cache",
            actions=[
                vm.Action(
                    function=empty_cache(),
                    inputs=["empty_button_id.n_clicks"],
                )
            ],
        ),
    ],
    controls=[
        vm.Filter(
            column="year",
            targets=["the_graph"],
            selector=vm.RangeSlider(
                title="Select timeframe",
            ),
        ),
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


if __name__ == "__main__":
    Vizro._user_assets_folder = os.path.abspath("../assets")
    # data_manager._cache.config = {
    #     "CACHE_TYPE": "FileSystemCache",
    #     "CACHE_DIR": "cache",
    #     "CACHE_THRESHOLD": 20,  # The maximum number of items the cache can hold
    #     "CACHE_DEFAULT_TIMEOUT": 3000,  # Unit of time is seconds
    # }
    data_manager._cache.config = {
        "CACHE_TYPE": "RedisCache",
        "CACHE_REDIS_URL": "redis://localhost:6379/0",
        "CACHE_DEFAULT_TIMEOUT": 60,
    }
    Vizro().build(dashboard).run()
    # Vizro().build(dashboard).run(
    #     threaded=False,
    #     processes=3,
    #     dev_tools_hot_reload=False
    # )
