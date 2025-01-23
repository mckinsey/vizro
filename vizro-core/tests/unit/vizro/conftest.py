"""Fixtures to be shared across several tests."""

import pandas as pd
import plotly.graph_objects as go
import pytest

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.figures import kpi_card
from vizro.tables import dash_ag_grid, dash_data_table


@pytest.fixture
def gapminder():
    return px.data.gapminder(datetimes=True)


@pytest.fixture
def stocks():
    return px.data.stocks()


@pytest.fixture
def gapminder_dynamic_first_n_last_n_function(gapminder):
    return lambda first_n=None, last_n=None: (
        pd.concat([gapminder[:first_n], gapminder[-last_n:]])
        if last_n
        else gapminder[:first_n]
        if first_n
        else gapminder
    )


@pytest.fixture
def standard_px_chart(gapminder):
    return px.scatter(
        data_frame=gapminder,
        x="gdpPercap",
        y="lifeExp",
        size="pop",
        color="continent",
        hover_name="country",
        size_max=60,
    )


@pytest.fixture
def scatter_params():
    return {"x": "gdpPercap", "y": "lifeExp"}


@pytest.fixture
def scatter_chart_dynamic_data_frame(scatter_params):
    return px.scatter("gapminder_dynamic_first_n_last_n", **scatter_params)


@pytest.fixture
def box_params():
    return {"x": "continent", "y": "lifeExp", "custom_data": ["continent"]}


@pytest.fixture
def box_chart_dynamic_data_frame(box_params):
    return px.box("gapminder_dynamic_first_n_last_n", **box_params)


@pytest.fixture
def standard_ag_grid(gapminder):
    return dash_ag_grid(data_frame=gapminder)


@pytest.fixture
def ag_grid_with_id(gapminder):
    return dash_ag_grid(id="underlying_ag_grid_id", data_frame=gapminder)


@pytest.fixture
def standard_dash_table(gapminder):
    return dash_data_table(data_frame=gapminder)


@pytest.fixture
def dash_data_table_with_id(gapminder):
    return dash_data_table(id="underlying_table_id", data_frame=gapminder)


@pytest.fixture
def standard_go_chart(gapminder):
    return go.Figure(data=go.Scatter(x=gapminder["gdpPercap"], y=gapminder["lifeExp"], mode="markers"))


@pytest.fixture
def standard_kpi_card(gapminder):
    return kpi_card(
        data_frame=gapminder,
        value_column="lifeExp",
        agg_func="mean",
        value_format="{value:.3f}",
    )


@pytest.fixture
def chart_with_temporal_data(stocks):
    return go.Figure(data=go.Scatter(x=stocks["Date"], y=stocks["AAPL.High"], mode="markers"))


@pytest.fixture()
def page_1():
    return vm.Page(title="Page 1", components=[vm.Button()])


@pytest.fixture()
def page_2():
    return vm.Page(title="Page 2", components=[vm.Button()])


@pytest.fixture
def managers_one_page_two_graphs_with_dynamic_data(box_chart_dynamic_data_frame, scatter_chart_dynamic_data_frame):
    """Instantiates a simple model_manager and data_manager with a page, two graph models and the button component."""
    vm.Page(
        id="test_page",
        title="My first dashboard",
        components=[
            vm.Graph(id="box_chart", figure=box_chart_dynamic_data_frame),
            vm.Graph(id="scatter_chart", figure=scatter_chart_dynamic_data_frame),
            vm.Button(id="button"),
        ],
    )
    Vizro._pre_build()


@pytest.fixture()
def vizro_app():
    """Fixture to instantiate Vizro/Dash app.

    Required if Vizro._pre_build or dashboard.pre_build is called since dash.register_page can only be called after
    app instantiation.pages.
    """
    return Vizro()
