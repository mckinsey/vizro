import pytest

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro


@pytest.fixture
def managers_one_page_two_graphs(gapminder):
    """Instantiates a simple model_manager and data_manager with a page, and two graph models and gapminder data."""
    vm.Page(
        id="test_page",
        title="My first dashboard",
        components=[
            vm.Graph(id="scatter_chart", figure=px.scatter(gapminder, x="lifeExp", y="gdpPercap")),
            vm.Graph(id="bar_chart", figure=px.bar(gapminder, x="country", y="gdpPercap")),
        ],
    )
    Vizro._pre_build()


@pytest.fixture
def managers_one_page_container_controls(gapminder):
    """Instantiates a simple model_manager and data_manager with a page, and two graph models and gapminder data."""
    vm.Page(
        id="test_container",
        title="My first dashboard",
        components=[
            vm.Container(
                title="",
                components=[
                    vm.Graph(id="scatter_chart", figure=px.scatter(gapminder, x="lifeExp", y="gdpPercap")),
                ],
                controls=[
                    vm.Filter(id="container_filter", column="continent", selector=vm.Checklist(value=["Europe"])),
                    vm.Parameter(
                        id="container_parameter",
                        targets=["scatter_chart.x"],
                        selector=vm.Checklist(options=["lifeExp", "gdpPercap", "pop"], value=["lifeExp"]),
                    ),
                ],
            ),
            vm.Graph(id="bar_chart", figure=px.bar(gapminder, x="country", y="gdpPercap")),
        ],
    )


@pytest.fixture
def managers_one_page_container_controls_invalid(gapminder):
    """Instantiates a simple model_manager and data_manager with a page, and two graph models and gapminder data."""
    vm.Page(
        id="test_container",
        title="My first dashboard",
        components=[
            vm.Container(
                id="container_1",
                title="",
                components=[
                    vm.Graph(id="scatter_chart", figure=px.scatter(gapminder, x="lifeExp", y="gdpPercap")),
                ],
                controls=[
                    vm.Filter(
                        id="container_filter_2", column="continent", selector=vm.Checklist(), targets=["bar_chart"]
                    ),
                ],
            ),
            vm.Container(
                title="", components=[vm.Graph(id="bar_chart", figure=px.bar(gapminder, x="country", y="gdpPercap"))]
            ),
        ],
    )
