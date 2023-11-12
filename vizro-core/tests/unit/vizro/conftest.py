"""Fixtures to be shared across several tests."""

import plotly.graph_objects as go
import pytest

import vizro.models as vm
import vizro.plotly.express as px
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
def page1():
    return vm.Page(title="Page 1", components=[vm.Button(), vm.Button()])


@pytest.fixture()
def page2():
    return vm.Page(title="Page 2", components=[vm.Button(), vm.Button()])


@pytest.fixture()
def dashboard(page1, page2):
    dashboard = vm.Dashboard(pages=[page1, page2])
    return dashboard


@pytest.fixture()
def dashboard_prebuild(dashboard):
    dashboard.pre_build()
