"""Fixtures to be shared across several tests."""
import plotly.graph_objects as go
import pytest

import vizro.models as vm
import vizro.plotly.express as px
from vizro.models.types import capture


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
def standard_go_chart(gapminder):
    return go.Figure(data=go.Scatter(x=gapminder["gdpPercap"], y=gapminder["lifeExp"], mode="markers"))


@pytest.fixture
def minimal_capture_chart(gapminder):
    @capture("graph")
    def _minimal_capture_chart(data_frame):
        return go.Figure()

    return _minimal_capture_chart(gapminder)


@pytest.fixture()
def two_pages():
    two_pages = [
        vm.Page(title="Page 1", components=[vm.Button(), vm.Button()]),
        vm.Page(title="Page 2", components=[vm.Button(), vm.Button()]),
    ]
    return two_pages


@pytest.fixture()
def dashboard(two_pages):
    dashboard = vm.Dashboard(pages=two_pages)
    return dashboard
