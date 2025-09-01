import pytest

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro


# Mock out set_props so we don't need to supply updated_props in the mock callback contexts used in these actions
# tests.
# TODO: maybe it would be better to include updated_props through a centralized way of creating a mock callback
#  context. Actions tests should be simplified and refactored in due course anyway.
@pytest.fixture(autouse=True)
def mock_set_props(mocker):
    mocker.patch("vizro.models._components.graph.set_props")


@pytest.fixture
def gapminder_2007(gapminder):
    return gapminder.query("year == 2007")


@pytest.fixture
def iris():
    return px.data.iris()


@pytest.fixture
def box_chart(gapminder_2007, box_params):
    return px.box(gapminder_2007, **box_params)


@pytest.fixture
def scatter_chart(gapminder_2007, scatter_params):
    return px.scatter(gapminder_2007, **scatter_params)


@pytest.fixture
def scatter_matrix_params():
    return {"dimensions": ["sepal_width", "sepal_length", "petal_width", "petal_length"]}


@pytest.fixture
def scatter_matrix_chart(iris, scatter_matrix_params):
    return px.scatter_matrix(iris, **scatter_matrix_params)


@pytest.fixture
def target_scatter_filtered_continent(request, gapminder_2007, scatter_params):
    continent = request.param
    data = gapminder_2007[gapminder_2007["continent"].isin(continent)]
    return px.scatter(data, **scatter_params)


@pytest.fixture
def target_box_filtered_continent(request, gapminder_2007, box_params):
    continent = request.param
    data = gapminder_2007[gapminder_2007["continent"].isin(continent)]
    return px.box(data, **box_params)


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
def managers_one_page_two_graphs_one_table_one_aggrid_one_button(
    box_chart, scatter_chart, dash_data_table_with_id, ag_grid_with_id
):
    """Instantiates a simple model_manager and data_manager with: page, graphs, table, aggrid and button component."""
    vm.Page(
        id="test_page",
        title="My first dashboard",
        components=[
            vm.Graph(id="box_chart", figure=box_chart),
            vm.Graph(id="scatter_chart", figure=scatter_chart),
            vm.Table(id="vizro_table", figure=dash_data_table_with_id),
            vm.AgGrid(id="ag_grid", figure=ag_grid_with_id),
            vm.Button(id="button"),
        ],
    )
    Vizro._pre_build()


@pytest.fixture
def managers_one_page_one_graph_with_dict_param_input(scatter_matrix_chart):
    """Instantiates a model_manager and data_manager with a page and a graph that requires a list input."""
    vm.Page(
        id="test_page",
        title="My first dashboard",
        components=[
            vm.Graph(id="scatter_matrix_chart", figure=scatter_matrix_chart),
        ],
    )
    Vizro._pre_build()
