import pytest

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro


@pytest.fixture
def gapminder_2007(gapminder):
    return gapminder.query("year == 2007")


@pytest.fixture
def box_params():
    return {"x": "continent", "y": "lifeExp", "custom_data": ["continent"]}


@pytest.fixture
def box_chart(gapminder_2007, box_params):
    return px.box(gapminder_2007, **box_params).update_layout(margin_t=24)


@pytest.fixture
def scatter_params():
    return {"x": "gdpPercap", "y": "lifeExp"}


@pytest.fixture
def scatter_chart(gapminder_2007, scatter_params):
    return px.scatter(gapminder_2007, **scatter_params).update_layout(margin_t=24)


@pytest.fixture
def target_scatter_filtered_continent(request, gapminder_2007, scatter_params):
    continent = request.param
    data = gapminder_2007[gapminder_2007["continent"].isin(continent)]
    return px.scatter(data, **scatter_params).update_layout(margin_t=24)


@pytest.fixture
def target_box_filtered_continent(request, gapminder_2007, box_params):
    continent = request.param
    data = gapminder_2007[gapminder_2007["continent"].isin(continent)]
    return px.box(data, **box_params).update_layout(margin_t=24)


@pytest.fixture
def managers_one_page_two_graphs_one_button(box_chart, scatter_chart):
    """Instantiates a simple model_manager and data_manager with a page, two graph models and the button component."""
    vm.Page(
        id="test_page",
        title="My first dashboard",
        components=[
            vm.Graph(id="box_chart", figure=box_chart),
            vm.Graph(id="scatter_chart", figure=scatter_chart),
            vm.Button(id="button"),
        ],
    )
    Vizro._pre_build()


@pytest.fixture
def managers_one_page_two_graphs_one_table_one_button(box_chart, scatter_chart, dash_data_table_with_id):
    """Instantiates a simple model_manager and data_manager with a page, two graph models and the button component."""
    vm.Page(
        id="test_page",
        title="My first dashboard",
        components=[
            vm.Graph(id="box_chart", figure=box_chart),
            vm.Graph(id="scatter_chart", figure=scatter_chart),
            vm.Table(id="vizro_table", figure=dash_data_table_with_id),
            vm.Button(id="button"),
        ],
    )
    Vizro._pre_build()
