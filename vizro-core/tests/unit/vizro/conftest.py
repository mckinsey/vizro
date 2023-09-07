"""Fixtures to be shared across several tests."""
import pytest

import vizro.models as vm
import vizro.plotly.express as px


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
