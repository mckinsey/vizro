"""Fixtures to be shared across several tests."""

import pytest
import vizro.plotly.express as px


@pytest.fixture
def gapminder():
    return px.data.gapminder()


# TODO add more common fixtures here
