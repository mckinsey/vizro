"""Example to show dashboard configuration."""
import os

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.managers import data_manager
from vizro.models.types import capture


def retrieve_gapminder():
    """This is a function that returns gapminder data."""
    return px.data.gapminder()


data_manager["gapminder"] = retrieve_gapminder


@capture("action")
def delete_memoized_cache(collapse_button_id_n_clicks):
    """Delete memoized cache."""
    if collapse_button_id_n_clicks:
        data_manager._cache.delete_memoized(data_manager._get_component_data, data_manager, "the_graph")
        # data_manager._cache.delete_memoized(data_manager._get_component_data, data_manager, "the_graph2")


page = vm.Page(
    title="test_page",
    components=[
        vm.Graph(
            figure=px.box(
                "gapminder",
                x="continent",
                y="lifeExp",
                color="continent",
                title="Distribution per continent",
            ),
            id="the_graph",
        ),
        # vm.Graph(
        #     figure=px.box(
        #         "gapminder",
        #         x="continent",
        #         y="lifeExp",
        #         color="continent",
        #         title="Distribution per continent",
        #     ),
        #     id="the_graph2",
        # ),
        # vm.Button(
        #     id="delete_button_id",
        #     text="delete_memoized_cache",
        #     actions=[
        #         vm.Action(
        #             function=delete_memoized_cache(),
        #             inputs=["collapse_button_id.n_clicks"],
        #             outputs=[],
        #         )
        #     ]
        # )
    ],
    controls=[
        vm.Filter(
            column="year",
            selector=vm.RangeSlider(
                title="Select timeframe",
            ),
        ),
    ],
)
dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro._user_assets_folder = os.path.abspath("../assets")
    Vizro._cache_config = {
        "CACHE_TYPE": "FileSystemCache",
        "CACHE_DIR": "cache",
        "CACHE_THRESHOLD": 20,  # The maximum number of items the cache can hold
        "CACHE_DEFAULT_TIMEOUT": 3000,  # Unit of time is seconds
    }
    Vizro().build(dashboard).run()
    # Vizro().build(dashboard).run(
    #     threaded=False,
    #     processes=3,
    #     dev_tools_hot_reload=False
    # )
