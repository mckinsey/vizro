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
