"""Fixtures to be shared across several tests."""

import dash
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
def page1():
    return vm.Page(title="Page 1", components=[vm.Button(), vm.Button()])


@pytest.fixture()
def page2():
    return vm.Page(title="Page 2", components=[vm.Button(), vm.Button()])


@pytest.fixture()
def two_pages(page1, page2):
    return [page1, page2]


@pytest.fixture()
def dashboard(two_pages):
    dashboard = vm.Dashboard(pages=two_pages)
    return dashboard


@pytest.fixture()
def dashboard_build(dashboard):
    yield dashboard.build()
    del dash.page_registry["Page 1"]
    del dash.page_registry["Page 2"]
