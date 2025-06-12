"""Fixtures to be shared across several tests."""

import pytest

import vizro.models as vm
import vizro.plotly.express as px
from vizro.actions import filter_interaction


@pytest.fixture
def filter_interaction_action():
    return vm.Action(function=filter_interaction())


@pytest.fixture
def managers_page_container_controls(gapminder):
    """Instantiates a simple model_manager and data_manager with a page, and two graph models and gapminder data."""
    vm.Page(
        id="test_container_page",
        title="My first dashboard",
        components=[
            vm.Container(
                id="test_container",
                title="",
                components=[
                    vm.Graph(id="scatter_chart", figure=px.scatter(gapminder, x="lifeExp", y="gdpPercap")),
                ],
                controls=[
                    vm.Filter(
                        id="container_filter_dropdown",
                        column="country",
                    ),
                ],
            ),
            vm.Graph(id="bar_chart", figure=px.bar(gapminder, x="country", y="gdpPercap")),
        ],
        controls=[
            vm.Filter(
                id="page_dropdown",
                column="country",
            ),
        ],
    )
