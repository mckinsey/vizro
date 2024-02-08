"""Fixtures to be shared across several tests."""

import plotly.graph_objects as go
import pytest

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.tables import dash_data_table


@pytest.fixture
def gapminder():
    return px.data.gapminder()


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
def standard_dash_table(gapminder):
    return dash_data_table(data_frame=gapminder)


@pytest.fixture
def dash_data_table_with_id(gapminder):
    return dash_data_table(id="underlying_table_id", data_frame=gapminder)


@pytest.fixture
def standard_go_chart(gapminder):
    return go.Figure(data=go.Scatter(x=gapminder["gdpPercap"], y=gapminder["lifeExp"], mode="markers"))


@pytest.fixture()
def page_1():
    return vm.Page(title="Page 1", components=[vm.Button()])


@pytest.fixture()
def page_2():
    return vm.Page(title="Page 2", components=[vm.Button()])


@pytest.fixture()
def vizro_app():
    """Fixture to instantiate Vizro/Dash app.

    Required if Vizro._pre_build or dashboard.pre_build is called since dash.register_page can only be called after
    app instantiation.pages.
    """
    return Vizro()
